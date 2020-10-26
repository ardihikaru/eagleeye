"""
	Script to capture frames sent by a specific IP. It uses TCP connection to communicate.
		Once captured, visualizes the frames and creates realtime results with using OpenCV library

	Creator:
		Muhammad Febrian Ardiansyah (mfardiansyah.eed08g@nctu.edu.tw)
"""
import cv2
import time
import imagezmq
import logging
import argparse

###

L = logging.getLogger(__name__)


###

def get_imagezmq(zmq_receiver):
	try:
		array_name, image = zmq_receiver.recv_image()
		tmp = array_name.split("-")
		frame_id = int(tmp[0])
		t0 = float(tmp[1])
		return True, frame_id, t0, image

	except Exception as e:
		L.error("[ERROR]: %s" % str(e))
		return False, None, None, None


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--zmq-host', type=str, default="localhost", help='Server Host IP')
	parser.add_argument('--zmq-port', type=str, default="5550", help='Server Host Port')
	parser.add_argument('--cv-title', type=str, default="EE-OpenCV", help='Title for the CV out windows')
	parser.add_argument('--cv-width', type=int, default=800, help='Window width of the OpenCV UI')
	parser.add_argument('--cv-height', type=int, default=550, help='height width of the OpenCV UI')

	opt = parser.parse_args()
	print(opt)

	# setup window configuration
	cv2.namedWindow(opt.cv_title, cv2.WND_PROP_FULLSCREEN)
	cv2.resizeWindow(opt.cv_title, opt.cv_width, opt.cv_height)  # Enter your size

	zmq_url = "tcp://{}:{}".format(opt.zmq_host, opt.zmq_port)
	L.warning("ZMQ URL: %s" % zmq_url)
	zmq_recv = imagezmq.ImageHub(open_port=zmq_url, REQ_REP=False)

	while True:
		# ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
		try:
			is_success, frame_id, t0_zmq, img = get_imagezmq(zmq_recv)
			t1_zmq = (time.time() - t0_zmq) * 1000
			if is_success:
				L.warning('Latency [Visualizer Capture] of frame-%s: (%.5fms)' % (str(frame_id), t1_zmq))
				cv2.imshow(opt.cv_title, img)

		except:
			print("No more frame to show.")
			break

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	# The following frees up resources and closes all windows
	cv2.destroyAllWindows()
