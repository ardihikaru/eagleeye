"""test_1_pub.py -- basic send images test using PUB/SUB message pattern.
A simple test program that uses imagezmq to send images to a receiving program
that will display the images.
Brief test instructions are in the receiving program: test_1_pub.py.
"""

import sys
import time
import numpy as np
import cv2
import imagezmq

import time
from libs.addons.redis.translator import redis_set, redis_get, pub
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

# Create an image sender in PUB/SUB (non-blocking) mode
# sender = imagezmq.ImageSender(connect_to='tcp://*:5555', REQ_REP=False)
sender = imagezmq.ImageSender(connect_to='tcp://127.0.0.1:5555', REQ_REP=False)
channel = "pub-image"
# ch_recv_sign = "pub-image-verify"

image_window_name = 'From Sender'
i = 0
is_ready = True
while is_ready:  # press Ctrl-C to stop image sending program
# while i < 2:  # press Ctrl-C to stop image sending program
# while redis_get(rc_data, "is_ready") == 1:  # press Ctrl-C to stop image sending program
    # Increment a counter and print it's current state to console

    # i = i + 1
    # print('Sending ' + str(i))

    # # Create a simple image
    # image = np.zeros((400, 400, 3), dtype='uint8')
    # green = (0, 255, 0)
    # cv2.rectangle(image, (50, 50), (300, 300), green, 5)
    #
    # # Add an incrementing counter to the image
    # cv2.putText(image, str(i), (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 4)

    # img_path = "data/out1.png"
    # # img_path = "data/chart.jpg"
    # frame = cv2.imread(img_path)

    max_frames = 57
    # for i in range(max_frames):
    # redis_set(rc_data, ch_recv_sign, True)
    while i < 57:
        # while not redis_get(rc_data, ch_recv_sign):
        #     print(" --- waiting ...")
        print("signal received: continue reading frames")
        # redis_set(rc_data, ch_recv_sign, False)

        # img_name = "out" + str(i+1) + ".png"
        # img_path = "data/5g-dive/57-frames/" + img_name

        fid = i+1
        if fid < 10:
            fid = "00" + str(fid)
        elif fid < 100:
            fid = "0" + str(fid)
        else:
            fid = str(fid)

        img_name = "hover_frame_" + fid + ".jpg"
        img_path = "data/5g-dive/hover/" + img_name
        frame = cv2.imread(img_path)

        # print(" >>>>>>> this frame:", frame.shape)

        ts = time.time()
        # sender.send_image(str(ts), frame)
        sender.send_image(str(ts), frame)
        # sender.send_image(str(ts), frame)
        t_recv = time.time() - ts
        # pub(rc_data, channel, json.dumps({"data": {
        #     "ts": ts
        # }}))
        pub(rc_data, channel, ts)
        # time.sleep(1)
        # time.sleep(0.003)
        is_ready = False
        print(".. [%d][time=%s] Sending image (1920 x 1080) in (%.5fs): %s " % ((i+1), str(ts), t_recv, img_name))

        i += 1
        if i == 56:
            print("i balik ke 0")
            i = 0

        # break
    # break

    # ts = time.time()
    # sender.send_image(str(ts), frame)
    # t_recv = time.time() - ts
    # # time.sleep(1)
    # # time.sleep(0.003)
    # is_ready = False
    # print(".. Sending image (1920 x 1080) in (%.5fs)" % t_recv)

print("selesai")

