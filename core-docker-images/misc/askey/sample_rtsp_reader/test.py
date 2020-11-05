import cv2
from concurrent.futures import ThreadPoolExecutor


def skipped_func(cap, frame_id):
    ret, frame = cap.read()
    if ret == True:
        print(">>> SKIP frame:", frame_id, frame.shape)


def ignored_frame(cap, frame_id):
    try:
        kwargs = {
            "cap": cap,
            "frame_id": frame_id,
        }
        executor.submit(skipped_func, **kwargs)
    except:
        print("\nError ignored.")
        pass

def captured_frame(cap, frame_id):
    ret, frame = cap.read()
    if ret == True:
        print(">>> READ frame:", frame_id, frame.shape)


executor = ThreadPoolExecutor(100)

path = 0
cap = cv2.VideoCapture(path)
frame_id = 0
while True:
    frame_id += 1
    if frame_id % 2 == 0:
        ignored_frame(cap, frame_id)
    else:
        captured_frame(cap, frame_id)
