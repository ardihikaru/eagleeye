import asab
from ext_lib.utils import get_json_template
import aiohttp
from ews.controllers.stream_reader.functions import validate_request_json, request_to_redisdb
from ext_lib.redis.my_redis import MyRedis
import cv2
from aiohttp.multipart import MultipartWriter
import time
from ext_lib.utils import get_current_time


class StreamReader(MyRedis):
    def __init__(self):
        super().__init__(asab.Config)
        self.cap = None

    def read(self, request_json):
        print(request_json)
        t0_validator = time.time()
        validate_request_json(request_json)
        t1_validator = (time.time() - t0_validator) * 1000
        print('[%s] Latency for Request Valication (%.3f ms)' % (get_current_time(), t1_validator))

        t0_request_saving = time.time()
        request_to_redisdb(self.rc, request_json)
        t1_request_saving = (time.time() - t0_request_saving) * 1000
        print('[%s] Latency for Saving Request data (%.3f ms)' % (get_current_time(), t1_request_saving))

        return aiohttp.web.json_response(get_json_template(True, request_json, -1, "OK"))

    async def video_feed(self, request_json):
        response = aiohttp.web.StreamResponse(
            status=200,
            reason='OK',
            headers={
                # 'Content-Type': 'multipart/x-mixed-replace;boundary={}'.format(my_boundary)
                'Content-Type': 'multipart/x-mixed-replace'
            }
        )
        camera = cv2.VideoCapture(request_json["uri"])  # use 0 for web camera
        while True:
            # frame = get_jpeg_frame()
            # Capture frame-by-frame
            success, frame = camera.read()  # read the camera frame
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
            # with MultipartWriter('image/jpeg', boundary=my_boundary) as mpwriter:
            with MultipartWriter('image/jpeg') as mpwriter:
                mpwriter.append(frame, {'Content-Type': 'image/jpeg'})
                await mpwriter.write(response, close_boundary=False)
            await response.drain()

    # def gen_frames(self, uri):  # generate frame by frame from camera
    #     camera = cv2.VideoCapture(uri)  # use 0 for web camera
    #     while True:
    #         # Capture frame-by-frame
    #         success, frame = camera.read()  # read the camera frame
    #         if not success:
    #             break
    #         else:
    #             ret, buffer = cv2.imencode('.jpg', frame)
    #             frame = buffer.tobytes()
    #             yield (b'--frame\r\n'
    #                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
