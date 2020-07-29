import asyncio
import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import get_current_time, pubsub_to_json
import time
from imutils.video import FileVideoStream
from ext_lib.image_loader.load_images import LoadImages
import cv2

###

L = logging.getLogger(__name__)


###


class ExtractorService(asab.Service):
    """
        A class to extract either: Video stream or tuple of images
    """

    def __init__(self, app, service_name="scheduler.ExtractorService"):
        super().__init__(app, service_name)

        # start pub/sub
        self.redis = MyRedis(asab.Config)
        # self._run()

        # params for extractor
        self.cap = None
        self.frame_id = 0
        # Special params: from YOLO's config items
        self.img_size = int(asab.Config["objdet:yolo"]["img_size"])
        self.half = bool(asab.Config["objdet:yolo"]["half"])
        self.source_folder_prefix = asab.Config["objdet:yolo"]["source_folder_prefix"]
        self.file_ext = asab.Config["objdet:yolo"]["file_ext"]

    async def extract_folder(self, config):
        print("#### I am extractor FODLER function from ExtractorService!")
        print(config)
        dataset = await self._read_from_folder(config)

        # Loop each frame
        print()
        for i in range(len(dataset)):
            self.frame_id += 1
            path, img, im0s, vid_cap = dataset[i][0], dataset[i][1], dataset[i][2], dataset[i][3]

            try:
                success, frame = True, im0s
                print("--- success:", self.frame_id, success, frame.shape)
                # if self._detection_handler(ret, frame, received_frame_id):
                #     break

            except Exception as e:
                print(" ---- e:", e)
                break

        print("\n[%s] No more frame to show." % get_current_time())

    async def _read_from_folder(self, config):
        """
            Capture images from the source path folder, then, store them in the local variable
        """
        # Set Dataloader
        unordered_dataset = LoadImages(config["uri"], img_size=self.img_size, half=self.half)
        # order image index
        return await self._get_ordered_img(config, unordered_dataset)

    async def _get_ordered_img(self, config, dataset):
        """
            Get ordered images
        """
        max_img = len(dataset)
        ordered_dataset = []
        for i in range(max_img):
            ordered_dataset.append([])

        i = 0
        for path, img, im0s, vid_cap in dataset:
            prefix = self.source_folder_prefix
            # removed_str = self.opt.source + prefix
            removed_str = config["uri"] + prefix
            real_frame_idx = int((path.replace(removed_str, "")).replace(self.file_ext, ""))
            real_idx = real_frame_idx - 1
            ordered_dataset[real_idx] = [path, img, im0s, vid_cap]
            i += 1

        return ordered_dataset


    async def extract_video_stream(self, config):
        print("#### I am extractor VIDEO STREAM function from ExtractorService!")
        print(config)
        try:
            self.cap = await self._set_cap(config)

            while await self._streaming():
                self.frame_id += 1
                success, frame = await self._read_frame()
                print("\n --- success:", self.frame_id, success, frame.shape)
        except Exception as e:
            print(" ---- >> e:", e)

    async def _set_cap(self, config):
        if bool(asab.Config["stream:config"]["thread"]):
            return FileVideoStream(config["uri"]).start()  # Thread-based video capture
        else:
            return cv2.VideoCapture(config["uri"])

    async def _streaming(self):
        if bool(asab.Config["stream:config"]["thread"]):
            return self.cap.more()
        else:
            return True

    async def _read_frame(self):
        if bool(asab.Config["stream:config"]["thread"]):
            return True, self.cap.read()
        else:
            return self.cap.read()
