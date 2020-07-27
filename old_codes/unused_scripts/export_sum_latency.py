from utils.utils import *
import matplotlib.patches as mpatches
from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.translator import redis_get, redis_set
import argparse

class Plot:
    def __init__(self, opt):
        self.opt = opt

    def run(self):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    opt = parser.parse_args()
    print(opt)

    Plot(opt).run()
