from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.translator import redis_get, redis_get_all_keys
import simplejson as json


class DataExporter(MyRedis):
    def __init__(self, opt):
        super().__init__()
        self.opt = opt
        self.prefix = "d" + str(opt.drone_id) + "-"  # e.g. "d1-" for drone_id=1

    def export_pih_coord(self):
        bbox_dict = {}
        bbox_db = self.rc_bbox.keys()
        for key in bbox_db:
            if "mbbox" in key and self.prefix in key:
                arr = key.split("-")
                # drone_id = arr[0].replace("d", "")
                frame_id = arr[1].replace("f", "")
                bbox = redis_get(self.rc_bbox, key)
                bbox_json = json.loads(bbox)
                bbox_dict[frame_id] = bbox_json

        print("Exporting `%d frames` into: `%s`" % (len(bbox_dict), self.opt.export_path))
        with open(self.opt.export_path, 'w') as fp:
            json.dump(bbox_dict, fp)
