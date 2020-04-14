#!/usr/bin/env python

# Source: https://stackoverflow.com/questions/42458475/sending-image-over-sockets-only-in-python-image-can-not-be-open

import random
import socket, select
from time import gmtime, strftime
from random import randint

import time
from libs.addons.redis.translator import redis_set, redis_get
from redis import StrictRedis
import json
from libs.settings import common_settings

rc_data = StrictRedis(
            host=common_settings["redis_config"]["hostname"],
            port=common_settings["redis_config"]["port"],
            password=common_settings["redis_config"]["password"],
            db=common_settings["redis_config"]["db_data"],
            decode_responses=True
)

imgcounter = 1
# basename = "image%s.png"
# basename = "data/5g-dive/57-frames/out1.png"
# basename = "data/coba.png"
# basename = "data/hasil%s.png"
basename = "data/hasil.png"

HOST = '127.0.0.1'
PORT = 6666

connected_clients_sockets = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(10)

connected_clients_sockets.append(server_socket)

print("Starting Server...")
i = 0
while True:

    read_sockets, write_sockets, error_sockets = select.select(connected_clients_sockets, [], [])

    # print("disini ...")
    for sock in read_sockets:
        i += 1
        # print("masuk for .. i=", i)

        if sock == server_socket:
            print("ini IF")

            sockfd, client_address = server_socket.accept()
            connected_clients_sockets.append(sockfd)

        else:
            try:

                data = sock.recv(4096)
                # data = sock.recv(1000*1000)
                # print(" >>> Dapatkan data ...")
                # txt = str(data)
                txt = None

                # decode only text-based data
                try:
                    txt = data.decode()
                except:
                    print("ini pasti gambar ..")
                    print("LEN data:", len(data))
                    pass

                if data:
                    print("masuk if")

                    # if data.startswith('SIZE'):
                    if txt is not None and 'SIZE' in txt:
                        tmp = txt.split()
                        print("tmp:", tmp)
                        size = int(tmp[1])

                        print('got size')

                        sock.sendall("GOT SIZE".encode())

                    # elif data.startswith('BYE'):
                    elif txt is not None and 'BYE' in txt:
                        print("ini BYE")
                        sock.shutdown()

                    else:
                        print("masuk ELSE ke file")

                        # myfile = open(basename % imgcounter, 'wb')
                        myfile = open(basename, 'wb')
                        myfile.write(data)

                        print("myfile: ", myfile)
                        print(" sini ..")

                        t_send = redis_get(rc_data, "udp-ts")
                        # data = sock.recv(40960000)
                        data = sock.recv(409600000)
                        t_recv = time.time() - t_send
                        print(".. Terima gambar in (%.3fs)" % t_recv)
                        if not data:
                            myfile.close()
                            break

                        print("mulai write ...")
                        myfile.write(data)
                        myfile.close()

                        sock.sendall("GOT IMAGE".encode())
                        sock.shutdown()
            except Exception as e:
                print("ERROR ...", e)
                sock.close()
                connected_clients_sockets.remove(sock)
                continue
        imgcounter += 1
server_socket.close()

