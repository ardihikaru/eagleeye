# Modified from: https://gist.github.com/jeffbass/ebf877e964c9a0b84272

import zmq
import numpy as np
import cv2


class SerializingSocket(zmq.Socket):
    """A class with some extra serialization methods

    send_array sends numpy arrays with metadata necessary
    for reconstructing the array on the other side (dtype,shape).
    Also sends array name for display with cv2.show(image).
    recv_array receives dict(array_name,dtype,shape) and an array
    and reconstructs the array with the correct shape and array name.
    """

    def send_array(self, A, array_name="NoName", flags=0, copy=True, track=False):
        """send a numpy array with metadata and array name"""
        md = dict(
            array_name=array_name,
            dtype=str(A.dtype),
            shape=A.shape,
        )
        self.send_json(md, flags | zmq.SNDMORE)
        return self.send(A, flags, copy=copy, track=track)

    def recv_array(self, flags=0, copy=True, track=False):
        """recv a numpy array, including array_name, dtype and shape"""
        md = self.recv_json(flags=flags)
        msg = self.recv(flags=flags, copy=copy, track=track)
        A = np.frombuffer(msg, dtype=md['dtype'])
        return (md['array_name'], A.reshape(md['shape']))


class SerializingContext(zmq.Context):
    _socket_class = SerializingSocket


class ZMQConnect:
    """ A class that opens a zmq REQ socket on the headless computer """

    def __init__(self, connect_to="tcp://127.0.0.1:5571"):
        """ initialize zmq socket for sending images to display on remote computer """
        """ connect_to is the tcp address:port of the display computer """
        self.zmq_context = SerializingContext()
        self.zmq_socket = self.zmq_context.socket(zmq.REQ)
        self.zmq_socket.connect(connect_to)

    def transfer_img(self, array_name, array, collect_resp=False):
        """send image to be printed on remote server"""
        if array.flags['C_CONTIGUOUS']:
            # if array is already contiguous in memory just send it
            self.zmq_socket.send_array(array, array_name, copy=False)
        else:
            # else make it contiguous before sending
            array = np.ascontiguousarray(array)
            self.zmq_socket.send_array(array, array_name, copy=False)
        message = None
        if collect_resp:
            message = self.zmq_socket.recv()

        print(">>> received MSG from server:", message)
        return message


class ZMQImageServer:
    """A class that opens a zmq REP socket on the Server computer to receive images """

    def __init__(self, open_port="tcp://127.0.0.1:5571"):
        """ initialize zmq socket on Server computer that will return images """
        self.zmq_context = SerializingContext()
        self.zmq_socket = self.zmq_context.socket(zmq.REP)
        self.zmq_socket.bind(open_port)

    def recv_img(self, copy=False, send_resp=False):
        """ receives and returns image data on the Server computer """
        array_name, image = self.zmq_socket.recv_array(copy=copy)
        print("Received Array Named: ", array_name)
        print("Array size: ", image.shape)
        if send_resp:
            self.zmq_socket.send(b"OK")
        return array_name, image
