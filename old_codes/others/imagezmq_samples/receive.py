"""test_1_sub.py -- basic receive images test in PUB/SUB mode.
A simple test program that uses imagezmq to receive images from a program that
is sending images. This test pair uses the PUB/SUB messaging pattern.
1. Run this program in its own terminal window:
python test_1_sub.py
There is no particular order in which sending and receiving scripts should be
run.
2.Run the image sending program in a different terminal window:
python test_1_pub.py
A cv2.imshow() window will appear showing the tramsmitted image. The sending
program sends images with an incrementing counter so you can see what is sent
and what is received.
If you terminate receiving script pay attention to the fact that sending script
will continue to increment and send images.
If you start receiving script again it will start picking images from the
current position.
To end the programs, press Ctrl-C in the terminal window of the sending program
first. Then press Ctrl-C in the terminal window of the receiving proram. You
may have to press Ctrl-C in the display window as well.
"""

import sys
import cv2
import imagezmq

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

id = 1
img_name = "view"
# print("is_ready: ", redis_get(rc_data, "is_ready"))
image_hub = imagezmq.ImageHub(open_port='tcp://127.0.0.1:5555', REQ_REP=False)
# image_hub = imagezmq.ImageHub(open_port='tcp://127.0.0.1:5551', REQ_REP=False)
# image_hub = imagezmq.ImageHub(open_port='tcp://127.0.0.1:5553', REQ_REP=False)
# channel = "pub-image"
channel = "stream_1"
# ch_recv_sign = "pub-image-verify"

pub_sub = rc_data.pubsub()
pub_sub.subscribe([channel])
is_listening = True
counter = 0
t0, t_now, t_recv = None, None, None
for item in pub_sub.listen():
    data = item["data"]
    # print("data: ", data)
    # print("data: ", type(data))
    # if "data" in item["data"] == 1:
    if isinstance(item["data"], int):
        print("lewati ..")
    else:
        counter += 1

        if counter == 1:
            t0 = time.time()
            # t_now = t0

        print(" ... masuk sini @ ", counter)
        try:
            print(" .... DAPET GAK YAA")
            image_name, image = image_hub.recv_image()
            print(" ..... DAPET nih..")

            # TO DO HERE ...
        except Exception as e:
            print("ada error ..", e)

        # t0 = time.time()
        # t_recv = t0 - float(image_name)
        # t_recv = time.time() - float(image_name)
        # print("type", type(item["data"]), item["data"])


        # t_recv = time.time() - float(item["data"])
        t_now = time.time()
        t_recv = t_now - t0

        print(">>>>> time t_now=%s vs t0=%s vs t_recv=%s: " % (str(t_now), str(t0), str(t_recv)))
        print(".. [%d] Received image (1920 x 1080) in (%.7fs)" % (id, t_recv))

        t0 = t_now
        # if counter > 0:
        #     t0 = t_now
            # t0 = t_recv

        # if counter == 1:
        #     t_recv = t_now - t0
        #     t0 = t_recv
        # else:
        #     t_recv = t_now - t0


        # print("t_recv: ", t_recv)
        # # print(">>>>> time: ", time.time(), item["data"], t_recv)
        # print(">>>>> time t_now=%s vs t0=%s vs t_recv=%s: " % (str(t_now), str(t0), str(t_recv)))
        # print(".. [%d] Received image (1920 x 1080) in (%.7fs)" % (id, t_recv))
        # time.sleep(0.05) # add 50ms @ YOLOv3 inference latency
        # time.sleep(0.02) # add 20ms @ other data handshaking latency

        t_0_cv = time.time()
        # cv2.imshow(img_name, image)
        # cv2.waitKey(100)  # wait until a key is pressed
        t_cv_recv = time.time() - t_0_cv
        # print(".. [%d] IM.SHOW in (%.7fs)" % (id, t_cv_recv))
        # cv2.imwrite("data/coba/hasil_%s.png" % image_name, image)

        # img_info = json.loads(item["data"])
        # t_recv = time.time() - img_info["data"]["ts"]
        # print("disini ..", type(data), data)

        # redis_set(rc_data, ch_recv_sign, True)
        id += 1

print("Finished listening")

    # if int(item["data"]) == 1:
    #     continue
    # if data["data"] == 9: # ok
    #     print(" ini data ok", item["data"]["data"])
    # else:
    #     continue
        # print("data awal")

# while True:  # press Ctrl-C to stop image display program
#     # t_send = redis_get(rc_data, "udp-ts")
#     print("@ ... while true")
#     image_name, image = image_hub.recv_image()
#     print(".. shape: ", image.shape)
#     t0 = time.time()
#     t_recv = t0 - float(image_name)
#     print(".. [%d][%s]-[%s] Received image (1920 x 1080) in (%.5fs)" % (id, image_name, str(t0), t_recv))
#     cv2.imshow(img_name, image)
#     # cv2.imwrite("data/hasil_%s.png" % image_name, image)
#     cv2.waitKey(1000)  # wait until a key is pressed
#     # cv2.waitKey(1)  # wait until a key is pressed
#     # id += 1
