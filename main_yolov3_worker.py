import argparse
from sys import platform

from models import *  # set ONNX_EXPORT in models.py
from utils.datasets import *
from utils.utils import *

from libs.algorithms.yolo_v3 import YOLOv3

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--drone_id', type=int, default=1, help='Drone ID')
    parser.add_argument('--node', type=str, default="1", help='Redis Subscriber channel')
    parser.add_argument('--plot_latency', type=bool, default=True, help='Save latency result into Graph')
    parser.add_argument('--latency_output', type=str, default="output/saved_latency/tmp",
                        help='Output location for latency results')

    parser.add_argument('--maximize_latency', type=bool, default=False,
                        help='Enable max latency (disabling some features)')

    # parser.add_argument('--txt_format', type=str, default='default', help='Output Txt Format')
    parser.add_argument('--txt_format', type=str, default='cartucho',
                        help='Output Txt Format') # Source https://github.com/Cartucho/mAP#running-the-code

    # MODv1 configuration
    parser.add_argument('--w_ratio', type=str, default=0.25, help='Width Ratio (for MB-Box Algorithm)')
    parser.add_argument('--h_ratio', type=float, default=0.1, help='Height Ratio (for MB-Box Algorithm)')

    parser.add_argument('--modv1', type=bool, default=False,
    # parser.add_argument('--modv1', type=bool, default=True,
                        help='Enabling/Disabling MOD Algorithm v1')
    parser.add_argument('--modv2', type=bool, default=True,
    # parser.add_argument('--modv2', type=bool, default=False,
                        help='Enabling/Disabling MOD Algorithm v2')

    parser.add_argument('--default_detection', type=bool, default=True,
                        help='Enabling/Disabling Default Box Bounding Algorithm')
    parser.add_argument('--mbbox_detection', type=bool, default=True,
                        help='Enabling/Disabling Merge Box Bounding Algorithm')
    parser.add_argument('--save_enlarged_img', type=bool, default=False,
                        help='Enabling/Disabling Save enlarged img')

    # Storing results
    parser.add_argument('--output_txt', type=str, default=False, help='output txt information')  # output folder
    parser.add_argument('--save_original_img', type=str, default=False, help='Enabling/Disabling Crop detected image')
    parser.add_argument('--save_crop_img', type=str, default=False, help='Enabling/Disabling Crop detected image')
    parser.add_argument('--save_bbox_img', type=str, default=False, help='Enabling/Disabling Store BBox image')
    parser.add_argument('--save_mbbox_img', type=str, default=False, help='Enabling/Disabling Store MBBox image')

    # Storage result directory
    parser.add_argument('--bbox_dir', type=str, default="output/bbox",
                        help='Raw image output')
    parser.add_argument('--frames_dir', type=str, default="output/original",
                        help='BBox image output')
    parser.add_argument('--mbbox_output', type=str, default="output/mbbox",
                        help='MMBox image output')
    parser.add_argument('--output', type=str, default='output', help='Root output folder')


    parser.add_argument('--cfg', type=str, default='yolo-obj-v5.cfg', help='*.cfg path')
    parser.add_argument('--names', type=str, default='data/obj.names', help='*.names path')
    parser.add_argument('--weights', type=str, default='weights/TM-07.weights', help='path to weights file')

    parser.add_argument('--source', type=str, default='', help='source')  # Not used, but do not delete it!

    parser.add_argument('--img_width', type=int, default=1920, help='Image Width')
    parser.add_argument('--img_height', type=int, default=1080, help='Image Height')

    # YOLO configuration; We trained the training data with 832 pixels (Tim's said)
    # parser.add_argument('--img-size', type=int, default=416, help='inference size (pixels)')
    parser.add_argument('--img-size', type=int, default=832, help='inference size (pixels)')
    # parser.add_argument('--img-size                               ', type=int, default=832, help='inference size (pixels)')  ## (3, 480, 832)
    # parser.add_argument('--img-size', type=int, default=1080, help='inference size (pixels)')  ## (3, 632, 1080)
    # parser.add_argument('--img-size', type=int, default=1920, help='inference size (pixels)')  ## (3, 1088, 1920)
                    # parser.add_argume                     nt('--img-size', type=int, default=832, help='inference size (pixels)')
    # parser.add_argument('--conf-thres', type=float, default=0.3, help='object confidence threshold')
    parser.add_argument('--conf-thres', type=float, default=0.1, help='object confidence threshold')
    # parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--iou-thres', type=float, default=0.1, help='IOU threshold for NMS')
    parser.add_argument('--fourcc', type=str, default='mp4v', help='output video codec (verify ffmpeg support)')
    parser.add_argument('--half', action='store_true', help='half precision FP16 inference')
    parser.add_argument('--device', default='', help='device id (i.e. 0 or 0,1) or cpu')
    parser.add_argument('--view-img', action='store_true', help='display results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    opt = parser.parse_args()
    # print(opt)

    with torch.no_grad():
        YOLOv3(opt).waiting_frames()
