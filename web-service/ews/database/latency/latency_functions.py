"""
    List of functions to manage actions (Create, Read, Update, Delete) of `Locations` data
"""

from mongoengine import DoesNotExist, NotUniqueError, Q, ValidationError
from ext_lib.utils import mongo_list_to_dict, mongo_dict_to_dict, pop_if_any, get_current_time
from datetime import datetime
import time
from ext_lib.redis.translator import redis_set


def insert_new_data(db_model, new_data, msg):
    try:
        inserted_data = db_model(**new_data).save()
    except ValidationError as e:
        return False, None, str(e)

    except NotUniqueError as e:
        return False, None, str(e)

    new_data["id"] = str(inserted_data.id)

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

    except Exception as e:
        return False, str(e)

    return True, "OK"


def upd_data_by_id(db_model, _id, new_data):
    try:
        pop_if_any(new_data, "id")
        db_model.objects.get(id=_id).update(**new_data)
    except Exception as e:
        return False, None, str(e)

    new_data["id"] = _id

    return True, new_data, None
