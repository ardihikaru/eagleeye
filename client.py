#!/usr/bin/env python

import random
import socket, select
from time import gmtime, strftime
from random import randint
import cv2 #Import openCV
import sys #import Sys. Sys will be used for reading from the command line. We give Image name parameter with extension when we will run python script

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

# image = "tux.png"
# image = "data/out1.png"
# image = "data/tulus.jpeg"
image = "data/wall.jpg"
# image = "data/coba.png"

HOST = '127.0.0.1'
PORT = 6666

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)
sock.connect(server_address)

try:

    # # Read the image. The first Command line argument is the image
    # my_image = cv2.imread(image)  # The function to read from an image into OpenCv is imread()
    # cv2.imshow("OpenCV Image Reading", my_image)
    # cv2.waitKey(0)

    # open image
    myfile = open(image, 'rb')
    bytes = myfile.read()
    size = len(bytes)
    print(">>> TYPE bytes: ", type(bytes))
    print(">> size:", size)
    msg = ("SIZE %s" % size).encode()

    # send image size to server
    sock.sendall(msg)
    # answer = sock.recv(4096)
    answer = (sock.recv(4096)).decode()

    print('answer = %s' % answer)

    try:
        redis_set(rc_data, "udp-ts", time.time())
        print(".. mulai sending gambar")
        sock.sendall(bytes)
        # sock.sendall("sending img".encode())
        print(" ... selesai sending gambr")

        # # check what server send
        # answer = sock.recv(4096)
        # # answer = sock.recv(1000 * 1000)
        # print('answer = %s' % answer)
        #
        # if answer == 'GOT IMAGE':
        #     sock.sendall("BYE BYE ".encode())
        #     print('Image successfully send to server')
    except Exception as e:
        print("ERROR .. ", e)

    # myfile.close()

finally:
    sock.close()

print("selesai ...")