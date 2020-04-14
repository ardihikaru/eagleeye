from __future__ import division

from models import *
from utils.utils import *
from utils.datasets import *

import os
import sys
import time
import datetime
import argparse

import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from torch.autograd import Variable

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import NullLocator
import cv2 as cv
from redis import StrictRedis
import json
from multiprocessing import Process

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_folder", type=str, default="data/samples", help="path to dataset")
    parser.add_argument("--img_size", type=int, default=416, help="size of each image dimension")
    # parser.add_argument("--source", type=str, default="data/5g-dive/customTest_MIRC-Roadside-5s.mp4", help="source")
    # parser.add_argument("--source", type=str, default="http://140.113.86.92:10000/drone-3.flv", help="source")
    # parser.add_argument("--source", type=str, default="http://140.113.86.92:10000/drone-2.flv", help="source")
    parser.add_argument("--source", type=str, default="http://140.113.86.92:10000/drone-1.flv", help="source")
    opt = parser.parse_args()
    print(opt)

    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # os.makedirs("output", exist_ok=True)

    # dataloader = DataLoader(
    #     ImageFolder(None, img_size=opt.img_size),
    #     batch_size=opt.batch_size,
    #     shuffle=False,
    #     num_workers=opt.n_cpu,
    # )

    rc = StrictRedis(
        host="localhost",
        port=6379,
        password="bismillah",
        db=0,
        decode_responses=True
    )

    # Ardi: Use video instead
    print("\nReading video:")
    # cap = cv.VideoCapture(opt.source)
    cv.namedWindow("Image", cv.WND_PROP_FULLSCREEN)
    cv.resizeWindow("Image", 1366, 768) # Enter your size
    prev_time = time.time()

    pubsub = rc.pubsub()
    pubsub.subscribe(['stream'])
    for item in pubsub.listen():
        try:
            fetch_data = json.loads(item['data'])
            print('Streamer collects : ', fetch_data)
        except:
            pass

    # cap.release()
    # cv.destroyAllWindows()

    print("\nENDED Reading video:")