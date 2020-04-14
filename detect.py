import argparse
from sys import platform

from models import *  # set ONNX_EXPORT in models.py
from utils.datasets import *
from utils.utils import *

from libs.algorithms.yolo_v3 import YOLOv3

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--frames_dir', type=str, default="output_frames", help='Frame by frame output')
    parser.add_argument('--plot_latency', type=bool, default=True, help='Save latency result into Graph')
    parser.add_argument('--latency_output', type=str, default="saved_latency/tmp", help='Output location for latency results')
    # parser.add_argument('--maximize_latency', type=bool, default=True, help='Enable max latency (disabling some features)')
    parser.add_argument('--maximize_latency', type=bool, default=False, help='Enable max latency (disabling some features)')
    # parser.add_argument('--txt_format', type=str, default='default', help='Output Txt Format')
    parser.add_argument('--txt_format', type=str, default='cartucho', help='Output Txt Format') # Source https://github.com/Cartucho/mAP#running-the-code
    parser.add_argument('--w_ratio', type=str, default=0.25, help='Width Ratio (for MB-Box Algorithm)')
    # parser.add_argument('--w_ratio', type=float, default=1.95, help='Width Ratio (for MB-Box Algorithm)')
    parser.add_argument('--h_ratio', type=float, default=0.1, help='Height Ratio (for MB-Box Algorithm)')

    parser.add_argument('--default_detection', type=str, default=False, help='Enabling/Disabling Default Box Bounding Algorithm')
    # parser.add_argument('--default_detection', type=bool, default=True, help='Enabling/Disabling Default Box Bounding Algorithm')
    parser.add_argument('--mbbox_detection', type=bool, default=True, help='Enabling/Disabling Merge Box Bounding Algorithm')
    # parser.add_argument('--mbbox_detection', type=str, default=False, help='Enabling/Disabling Merge Box Bounding Algorithm')

    parser.add_argument('--crop_img', type=str, default=True, help='Enabling/Disabling Crop detected image')
    # parser.add_argument('--crop_img', type=str, default=False, help='Enabling/Disabling Crop detected image')
    # parser.add_argument('--cfg', type=str, default='cfg/yolov3-spp.cfg', help='*.cfg path')
    parser.add_argument('--cfg', type=str, default='yolo-obj-v5.cfg', help='*.cfg path')
    # parser.add_argument('--names', type=str, default='data/coco.names', help='*.names path')
    parser.add_argument('--names', type=str, default='data/obj.names', help='*.names path')
    # parser.add_argument('--weights', type=str, default='weights/yolov3-spp.weights', help='path to weights file')
    parser.add_argument('--weights', type=str, default='weights/TM-04.weights', help='path to weights file')
    # parser.add_argument('--source', type=str, default='data/samples', help='source')  # input file/folder, 0 for webcam
    # parser.add_argument('--source', type=str, default='data/5g-dive/error', help='source')  # input file/folder, 0 for webcam
    # parser.add_argument('--source', type=str, default='data/5g-dive/57-frames', help='source')  # input file/folder, 0 for webcam
    # parser.add_argument('--source', type=str, default='data/5g-dive/sample-n-frames', help='source')  # input file/folder, 0 for webcam
    # parser.add_argument('--source', type=str, default='data/5g-dive/sample-4-frames', help='source')  # input file/folder, 0 for webcam
    # parser.add_argument('--source', type=str, default='data/5g-dive/sample-1-frame', help='source')  # input file/folder, 0 for webcam
    # parser.add_argument('--source', type=str, default='data/5g-dive/false-frame', help='source')  # input file/folder, 0 for webcam
    # parser.add_argument('--source', type=str, default='data/5g-dive/customTest_MIRC-Roadside-5s-frame-rev-PersonFlag', help='source')  # input file/folder, 0 for webcam
    # parser.add_argument('--source', type=str, default='data/5g-dive/videos/customTest_MIRC-Roadside-5s.mp4', help='source')  # input file/folder, 0 for webcam
    # parser.add_argument('--source', type=str, default='http://140.113.86.92:10000/drone-3.flv', help='source')  # input file/folder, 0 for webcam
    parser.add_argument('--source', type=str, default='http://140.113.86.92:10000/drone-2.flv', help='source')  # input file/folder, 0 for webcam
    # parser.add_argument('--source', type=str, default='http://140.113.86.92:10000/drone-1.flv', help='source')  # input file/folder, 0 for webcam
    parser.add_argument('--output', type=str, default='output', help='output folder')  # output folder
    # parser.add_argument('--img-size', type=int, default=416, help='inference size (pixels)')
    parser.add_argument('--img-size', type=int, default=832, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.3, help='object confidence threshold')
    # parser.add_argument('--conf-thres', type=float, default=0.1, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    # parser.add_argument('--iou-thres', type=float, default=0.1, help='IOU threshold for NMS')
    parser.add_argument('--fourcc', type=str, default='mp4v', help='output video codec (verify ffmpeg support)')
    parser.add_argument('--half', action='store_true', help='half precision FP16 inference')
    parser.add_argument('--device', default='', help='device id (i.e. 0 or 0,1) or cpu')
    parser.add_argument('--view-img', action='store_true', help='display results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    opt = parser.parse_args()
    print(opt)

    with torch.no_grad():
        YOLOv3(opt).run()
        # detect()
