import cv2
import numpy as np
from math import sqrt
from scipy.spatial import distance
from yolo_app.etc.config import config


def crop_image(save_path, img, xywh):
    x = xywh[0]
    y = xywh[1]
    w = xywh[2]
    h = xywh[3]
    crop_img = img[y:y + h, x:x + w]
    cv2.imwrite(save_path, crop_img)


def np_xyxy2xywh(xyxy, data_type=int):
    # Convert bounding box format from [x1, y1, x2, y2] to [x, y, w, h]
    xywh = np.zeros_like(xyxy)
    x1 = xyxy[0]
    y1 = xyxy[1]
    x2 = xyxy[2]
    y2 = xyxy[3]

    xywh[0] = xyxy[0]
    xywh[1] = xyxy[1]
    xywh[2] = data_type(abs(x2 - x1))
    xywh[3] = data_type(abs(y1 - y2))
    return xywh


def torch2np_xyxy(xyxy, data_type=int):
    # Convert bounding box format from [x1, y1, x2, y2] to [x, y, w, h]

    # CPU Mode
    try:
        np_xyxy = np.zeros_like(xyxy)
    # GPU Mode
    except:
        np_xyxy = np.zeros_like(xyxy.data.cpu().numpy())

    np_xyxy[0] = data_type(xyxy[0])
    np_xyxy[1] = data_type(xyxy[1])
    np_xyxy[2] = data_type(xyxy[2])
    np_xyxy[3] = data_type(xyxy[3])

    return np_xyxy


def get_det_xyxy(det):
    numpy_xyxy = torch2np_xyxy(det[:4])
    return numpy_xyxy


# Merged of 2 bounding boxes (xyxy and xyxy)
def get_mbbox(obj_1, obj_2):
    box1_x1 = obj_1[0]
    box1_y1 = obj_1[1]
    box1_x2 = obj_1[2]
    box1_y2 = obj_1[3]

    box2_x1 = obj_2[0]
    box2_y1 = obj_2[1]
    box2_x2 = obj_2[2]
    box2_y2 = obj_2[3]

    mbbox = [
        min(box1_x1, box2_x1),
        min(box1_y1, box2_y1),
        max(box1_x2, box2_x2),
        max(box1_y2, box2_y2)
    ]
    return mbbox


def np_xyxy2centroid(xyxy):
    centroid_x = (xyxy[0] + xyxy[2]) / 2
    centroid_y = (xyxy[1] + xyxy[3]) / 2
    return np.asarray([centroid_x, centroid_y])


def get_xyxy_distance(xyxy_1, xyxy_2):
    o1cx_o2cx = pow((xyxy_1[0] - xyxy_2[0]), 2)
    o1cy_o2cy = pow((xyxy_1[1] - xyxy_2[1]), 2)
    dist = sqrt(o1cx_o2cx + o1cy_o2cy)
    return dist


def get_xyxy_distance_manhattan(xyxy_1, xyxy_2):
    o1cx_o2cx = pow((xyxy_1[0] - xyxy_2[0]), 2)
    o1cy_o2cy = pow((xyxy_1[1] - xyxy_2[1]), 2)
    dist = sqrt(distance.cityblock(o1cx_o2cx, o1cy_o2cy))
    return dist


def save_txt(save_path, txt_format, bbox_xyxy=None, w_type='a', img_ext=".png", cls=None, conf=1.0):
    txt_path = save_path.replace(img_ext, '')
    with open(txt_path + '.txt', w_type) as file:
        if bbox_xyxy is None:
            file.write("")
        else:
            if cls is None:
                cls = config["bbox_config"]["default_label"]
            if txt_format == "default":
                file.write(('%g ' * 6 + '\n') % (bbox_xyxy, cls, conf))
            elif txt_format == "cartucho":
                str_output = cls + " "
                str_output += str(conf) + " "
                str_output += str(int(bbox_xyxy[0])) + " " + \
                              str(int(bbox_xyxy[1])) + " " + \
                              str(int(bbox_xyxy[2])) + " " + \
                              str(int(bbox_xyxy[3])) + "\n"

                file.write(str_output)
            else:
                pass
