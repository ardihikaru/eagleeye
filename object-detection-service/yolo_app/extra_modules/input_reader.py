from imutils.video import FileVideoStream
from yolo_app.components.utils.datasets import *


class InputReader:
    def __init__(self, opt):
        self.opt = opt

        # Init some default values
        self.is_running = True  # to keep reconnecting the connection with video stream
        self.cap = None
        self.dataset = None  # dataset for images from a folder

    def _read_from_folder(self):
        """
            Capture images from the source path folder, then, store them in the local variable
        """
        # Set Dataloader
        unordered_dataset = LoadImages(self.opt.source, img_size=self.opt.img_size, half=self.opt.half)
        # order image index
        self.dataset = self._get_ordered_img(unordered_dataset)

    def _get_ordered_img(self, dataset):
        """
            Get ordered images
        """
        max_img = len(dataset)
        ordered_dataset = []
        for i in range(max_img):
            ordered_dataset.append([])

        i = 0
        for path, img, im0s, vid_cap in dataset:
            prefix = self.opt.source_folder_prefix
            removed_str = self.opt.source + prefix
            real_frame_idx = int((path.replace(removed_str, "")).replace(self.opt.file_ext, ""))
            real_idx = real_frame_idx - 1
            ordered_dataset[real_idx] = [path, img, im0s, vid_cap]
            i += 1

        return ordered_dataset

    def _read_from_streaming(self):
        """
            Initial values for video streaming input
        """
        self.cap = FileVideoStream(self.opt.source).start()  # Thread-based video capture

    # def _stop_stream_listener(self):
    #     """
    #         Release resources
    #     """
    #     self.cap.release()
