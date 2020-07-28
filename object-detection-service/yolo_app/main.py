from __future__ import division
import argparse
from yolo_app.app import YOLOApp

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Enable CV out if enabled!
    parser.add_argument('--enable-cv-out', dest='cv_out', action='store_true', help="Enable/disable CV Out results")
    parser.add_argument('--window-size-height', type=int, default=1920, help="Window size: Height")
    parser.add_argument('--window-size-width', type=int, default=1080, help="Window size: Width")

    # YOLOv3 default configuration
    parser.add_argument('--device', default='', help='device id (i.e. 0 or 0,1) or cpu')
    parser.add_argument('--half', action='store_true', help='half precision FP16 inference')
    # parser.add_argument("--img_size", type=int, default=832, help="size of each image dimension")
    # parser.add_argument("--img_size", type=int, default=416, help="size of each image dimension")
    parser.add_argument("--img_size", type=int, default=416, help="size of each image dimension")
    parser.add_argument('--conf-thres', type=float, default=0.1, help='object confidence threshold')
    # parser.add_argument('--conf-thres', type=float, default=0.3, help='object confidence threshold')
    # parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--iou-thres', type=float, default=0.1, help='IOU threshold for NMS')
    parser.add_argument('--fourcc', type=str, default='mp4v', help='output video codec (verify ffmpeg support)')
    parser.add_argument('--view-img', action='store_true', help='display results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--names', type=str, default='./yolo_app/components/data/coco.names', help='*.names path')

    # Load YOLO config file
    parser.add_argument('--cfg', type=str, default='./yolo_app/components/cfg/yolov3.cfg', help='*.cfg path')
    # parser.add_argument('--cfg', type=str, default='./yolo_app/components/cfg/yolov3-tiny.cfg', help='*.cfg path')

    # Load weights
    parser.add_argument('--weights', type=str, default='./yolo_app/components/weights/yolov3.weights',
    # parser.add_argument('--weights', type=str, default='./yolo_app/components/weights/yolov3-tiny.weights',
                        help='path to weights file')

    # To define input source type: "folder" or "stream"; The default is "stream"
    parser.add_argument('--source-type-folder', action='store_false', dest='is_source_stream',
                        help="Type of source data (Folder or Stream)")
    parser.set_defaults(is_source_stream=True)

    # Used only when is_source_stream=True (Stream), otherwise it's not used
    parser.add_argument("--source_folder_prefix", type=str, default="out", help="source folder prefix")
    parser.add_argument("--file_ext", type=str, default=".png", help="source folder extension (png, jpg, ...)")

    # parser.add_argument("--source", type=str, default="data/images/sample-1-frame/", help="source")
    # parser.add_argument("--source", type=str, default="data/images/sample-4-frames/", help="source")
    parser.add_argument("--source", type=str, default="data/videos/customTest_MIRC-Roadside-5s.mp4", help="source")
    # parser.add_argument("--source", type=str, default="rtmp://140.113.86.92/live/demo", help="source")

    # To define the ROOT location to save any output results: Images, txt, graph, etc.
    parser.add_argument("--output", type=str, default="outputs/", help="path to export any results")

    # To enable/disable auto restart (Input as Video file or Streaming with RTSP/RTMP)
    parser.add_argument('--auto-restart', dest='is_auto_restart', action='store_true', help="To automatically restart")

    # Saving raw images
    parser.add_argument('--dump-raw-img', dest='dump_raw_img', action='store_true',
                        help="Enable/disable raw images dump")
    # parser.set_defaults(raw_img_dump=True)

    # Saving BBox images
    parser.add_argument('--dump-bbox-img-', dest='dump_bbox_img', action='store_true',
                        help="Enable/disable BBox images dump")
    # parser.set_defaults(bbox_img_dump=True)

    # Saving crop images
    parser.add_argument('--dump-crop-img', dest='dump_crop_img', action='store_true',
                        help="Enable/disable crop images dump")

    # Saved txt format: # Source https://github.com/Cartucho/mAP#running-the-code
    parser.add_argument('--txt_format', type=str, default='cartucho', help='Output Txt Format')

    # To enable/disable Input Reader limiter
    parser.add_argument('--is_limited', action='store_true',
                        help='Set True to stop the program forcefully after capturing `<max_frames>` frames ')
    parser.add_argument('--max_frames', type=int, default=5, help='Max Frames; Ignored when `is_limited`=False')

    opt = parser.parse_args()
    print(opt)

    YOLOApp(opt).run()
