"""
    List of functions to manage actions (Create, Read, Update, Delete) of `Nodes` data
"""

from mongoengine import DoesNotExist, NotUniqueError, Q, ValidationError
from ext_lib.utils import mongo_list_to_dict, mongo_dict_to_dict, pop_if_any, get_current_time
from datetime import datetime
from ext_lib.redis.translator import pub
import time
import simplejson as json
from ext_lib.redis.translator import redis_set


def insert_new_data(db_model, new_data, msg):
    try:
        inserted_data = db_model(**new_data).save()

    except ValidationError as e:
        return False, None, str(e)

    except NotUniqueError as e:
        return False, None, str(e)

    new_data["id"] = str(inserted_data.id)
    new_data["created_at"] = inserted_data.created_at.strftime("%Y-%m-%d, %H:%M:%S")
    new_data["updated_at"] = inserted_data.updated_at.strftime("%Y-%m-%d, %H:%M:%S")

    if len(new_data) > 0:
        return True, new_data, msg
    else:
        return False, None, msg


# variable `args` usage can be used later to filter the given results
def get_all_data(db_model, args=None):
    try:
        data = db_model.objects().to_json()
    except DoesNotExist:
        return False, None, 0
    data_dict = mongo_list_to_dict(data)

    if len(data_dict) > 0:
        return True, data_dict, len(data_dict)
    else:
        return False, None, 0


def get_data_by_id(db_model, _id):
    try:
        data = db_model.objects.get(id=_id).to_json()
    except Exception as e:
        return False, None, str(e)

    dict_data = mongo_dict_to_dict(data)

    return True, dict_data, None


def get_data_by_consumer(db_model, consumer):
    try:
        data = db_model.objects.get(consumer=consumer).to_json()
    except Exception as e:
        return False, None

    dict_data = mongo_dict_to_dict(data)

    return True, dict_data


def del_data_by_id(db_model, _id, rc):
    try:
        db_model.objects.get(id=_id).delete()

        # once successfully created, try sending information into Object Detection Service
        # channel = "node-" + _id + "-killer"
        channel = "node-" + _id
        # send data into Scheduler service through the pub/sub
        t0_publish = time.time()
        # dump_request = json.dumps({"active": False})
        # pub(rc, channel, dump_request)
        # Use redis key-value instead of pub/sub!
        redis_set(rc, channel, True)
        t1_publish = (time.time() - t0_publish) * 1000
        # TODO: Saving latency for scheduler:producer:destroy
        print('[%s] Latency to send a notification to destroy Object Detection Service (%.3f ms)' %
              (get_current_time(), t1_publish))

    except Exception as e:
        return False, str(e)

    return True, None


def upd_data_by_id(db_model, _id, new_data):
    try:
        pop_if_any(new_data, "id")
        db_model.objects.get(id=_id).update(**new_data)
    except Exception as e:
        return False, None, str(e)

    new_data["id"] = _id
    new_data["updated_at"] = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")

    return True, new_data, None
