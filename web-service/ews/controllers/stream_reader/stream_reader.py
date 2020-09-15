import asab
from ext_lib.utils import get_json_template
import aiohttp
from ews.controllers.stream_reader.functions import request_to_config, config_to_mongodb, get_config_data, \
    get_config_by_id, upd_config_by_id, del_config_by_id
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import pub
import time
from ext_lib.utils import get_current_time
from concurrent.futures import ThreadPoolExecutor
import simplejson as json
import logging

###

L = logging.getLogger(__name__)


###


class StreamReader:
    def __init__(self):
        self.executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))
        self.redis = MyRedis(asab.Config)

    def read(self, request_json):
        # Validate input
        # print(request_json)
        t0_validator = time.time()
        config = request_to_config(request_json)
        t1_validator = (time.time() - t0_validator) * 1000
        # print('[%s] Latency for Request Validation (%.3f ms)' % (get_current_time(), t1_validator))
        L.warning('[%s] Latency for Request Validation (%.3f ms)' % (get_current_time(), t1_validator))

        # send data into Scheduler service through the pub/sub
        t0_publish = time.time()
        # print("# send data into Scheduler service through the pub/sub")
        config["timestamp"] = time.time()  # To verify the communication latency
        dump_request = json.dumps(config)
        pub(self.redis.get_rc(), asab.Config["pubsub:channel"]["scheduler"], dump_request)
        t1_publish = (time.time() - t0_publish) * 1000
        config.pop("timestamp")  # removed, since it is a temporary key
        # TODO: Saving latency for scheduler:producer
        # print('[%s] Latency for Publishing data (%.3f ms)' % (get_current_time(), t1_publish))
        L.warning('[%s] Latency for Publishing data (%.3f ms)' % (get_current_time(), t1_publish))

        # save input into mongoDB through thread process
        # print("# save input into mongoDB through thread process")
        L.warning("# save input into mongoDB through thread process")
        config_to_mongodb(self.executor, config)

        # t0_request_saving = time.time()
        # request_to_redisdb(self.rc, request_json)
        # t1_request_saving = (time.time() - t0_request_saving) * 1000
        # print('[%s] Latency for Saving Request data (%.3f ms)' % (get_current_time(), t1_request_saving))

        # t0_saving_mongo = time.time()
        # is_success, config_data, msg = insert_new_data(ConfigModel, request_json)
        # t1_saving_mongo = (time.time() - t0_saving_mongo) * 1000
        # print(" -- config_data:", config_data)
        # print('[%s] Latency for Saving data into MongoDB (%.3f ms)' % (get_current_time(), t1_saving_mongo))

        # t0_loading_mongo = time.time()
        # is_success, config_data, msg = get_data_by_id(ConfigModel, config_data["id"])
        # t1_loading_mongo = (time.time() - t0_loading_mongo) * 1000
        # print('[%s] Latency for Loading data into MongoDB (%.3f ms)' % (get_current_time(), t1_loading_mongo))
        #
        # t0_deleting_mongo = time.time()
        # _, _ = del_data_by_id(ConfigModel, config_data["id"])
        # t1_deleting_mongo = (time.time() - t0_deleting_mongo) * 1000
        # print('[%s] Latency for Deleting data into MongoDB (%.3f ms)' % (get_current_time(), t1_deleting_mongo))

        # t0_publish = time.time()
        # channel = "scheduler"
        # # pub(self.rc, channel, request_json)
        # pub(self.redis.get_rc(), channel, request_json)
        # t1_publish = (time.time() - t0_publish) * 1000
        # print('[%s] Latency for Publishing data (%.3f ms)' % (get_current_time(), t1_publish))

        return aiohttp.web.json_response(get_json_template(True, request_json, -1, "OK"))

    async def get_data(self):
        is_success, config, total, msg = get_config_data()
        return aiohttp.web.json_response(get_json_template(is_success, config, total, msg))

    def delete_data_by_id_one(self, _id):
        return del_config_by_id(_id)
        # return get_json_template(True, {}, -1, "OK")

    def update_data_by_id(self, _id, json_data):
        return upd_config_by_id(_id, json_data)
        # return get_json_template(is_success, user_data, -1, msg)

    def get_data_by_id(self, _id):
        return get_config_by_id(_id)
        # return get_json_template(is_success, user_data, -1, msg)

    # async def video_feed(self, request_json):
    #     response = aiohttp.web.StreamResponse(
    #         status=200,
    #         reason='OK',
    #         headers={
    #             # 'Content-Type': 'multipart/x-mixed-replace;boundary={}'.format(my_boundary)
    #             'Content-Type': 'multipart/x-mixed-replace'
    #         }
    #     )
    #     camera = cv2.VideoCapture(request_json["uri"])  # use 0 for web camera
    #     while True:
    #         # frame = get_jpeg_frame()
    #         # Capture frame-by-frame
    #         success, frame = camera.read()  # read the camera frame
    #         if not success:
    #             break
    #         else:
    #             ret, buffer = cv2.imencode('.jpg', frame)
    #             frame = buffer.tobytes()
    #         # with MultipartWriter('image/jpeg', boundary=my_boundary) as mpwriter:
    #         with MultipartWriter('image/jpeg') as mpwriter:
    #             mpwriter.append(frame, {'Content-Type': 'image/jpeg'})
    #             await mpwriter.write(response, close_boundary=False)
    #         await response.drain()

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
