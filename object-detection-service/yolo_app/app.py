from yolo_app.extra_modules.input_reader import InputReader
import time
from yolo_app.components.utils.utils import get_current_time
from yolo_app.detection_algorithms.yolo_v3 import YOLOv3 as YOLO
import cv2 as cv


class YOLOApp(InputReader):
    def __init__(self, opt):
        super().__init__(opt)
        self.yolo = YOLO(self.opt)
        self.opt = opt

        self.window_name = "YOLOv3"

    def run(self):
        print("[%s] YOLO App is running now ..." % get_current_time())
        if not self.opt.is_source_stream:
            print("\n[%s] Reading folder data from path: `%s`" % (get_current_time(), self.opt.source))
            self._read_from_folder()  # it prints the collected image paths
            self._detect_from_folder()
        else:
            print("\n[%s] Reading video streaming from URL: `%s`" % (get_current_time(), self.opt.source))

            while self.is_running:
                try:
                    self._read_from_streaming()
                    self._detect_from_video_streaming()
                except:
                    print("\nUnable to communicate with the Streaming. Restarting . . .")

    def _detect_from_folder(self):
        for i in range(len(self.dataset)):
            received_frame_id, path, img, im0s, vid_cap = (i + 1), self.dataset[i][0], self.dataset[i][1], \
                                                          self.dataset[i][2], self.dataset[i][3]

            # ret = a boolean return value from getting the frame,
            # frame = the current frame being projected in the video
            try:
                ret, frame = True, im0s
                if self._detection_handler(ret, frame, received_frame_id):
                    break

            except Exception as e:
                print(" ---- e:", e)
                break

        print("\n[%s] No more frame to show." % get_current_time())

    def _initialize_visualizer(self):
        if self.opt.cv_out:
            # Set Window
            cv.namedWindow(self.window_name, cv.WND_PROP_FULLSCREEN)
            cv.moveWindow(self.window_name, 0, 0)

            # Set Window Position
            cv.moveWindow(self.window_name, 0, 0)

            # Set Window Size
            width = self.opt.window_size_height
            height = self.opt.window_size_width
            cv.resizeWindow(self.window_name, width, height)

    def _show_visual_results(self, frame):
        # show the frame with BBox
        cv.imshow(self.window_name, frame)
        cv.waitKey(1)

    def _detect_from_video_streaming(self):
        self._initialize_visualizer()

        received_frame_id = 0
        while (self.cap.more()) and self.is_running:
            received_frame_id += 1
            # ret = a boolean return value from getting the frame,
            # frame = the current frame being projected in the video
            try:
                ret = True
                frame = self.cap.read()

                is_break = self._detection_handler(ret, frame, received_frame_id)

                self._show_visual_results(frame)

                if is_break:
                    break

            except:
                if not self.opt.is_auto_restart:
                    print("\nStopping the system (3 seconds delay) . . .")
                    time.sleep(3)
                    self.is_running = False
                # Read this code ONLY when (1) is streaming through (2) RTSP/RTMP protocol
                elif self.opt.is_source_stream and self.opt.is_auto_restart:
                    print("\nStopping the system for a while (3 seconds delay) . . .")
                    time.sleep(3)
                else:
                    print("No more frame to show.")

                break

    def _detection_handler(self, ret, img0, frame_id):
        is_break = False

        if ret and not is_break:
            # Force stop after n frames; disabled when self.max_frames == 0
            if self.opt.is_limited and frame_id == (self.opt.max_frames + 1):
                print("\n[%s] Detection is automatically halted; Total processed frames: `%s frames`" %
                      (get_current_time(), (frame_id-1)))
                self.is_running = False
                is_break = True

            if not is_break:
                # Feed this image into YOLO network
                print("\n[%s] Feed frame-%s into YOLO network" % (get_current_time(), str(frame_id)))
                self.yolo.detect(img0, frame_id)

        else:
            print("IMAGE is INVALID.")
            print("I guess there is no more frame to show.")
            is_break = True

        return is_break
