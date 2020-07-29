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


class ResizerService(asab.Service):
    """
        A class to resize images, i.e. from FullHD into padded size (for YOLO)
    """

    def __init__(self, app, service_name="scheduler.ResizerModule"):
        super().__init__(app, service_name)

        # Special params: from YOLO's config items
        self.img_size = int(asab.Config["objdet:yolo"]["img_size"])

    async def gpu_convert_to_padded_size(self, img):
        print("#### I am extractor FODLER function from ExtractorService!")
        pass
