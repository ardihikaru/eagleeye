"""
    List of functions to manage actions (Create, Read, Update, Delete) of `Users` data
"""

import asab
from mongoengine import DoesNotExist, NotUniqueError, Q, ValidationError
from ext_lib.utils import mongo_list_to_dict, mongo_dict_to_dict, pop_if_any
from datetime import datetime
import jwt
from datetime import timedelta


def insert_new_data(db_model, new_data, msg):
    try:
        new_data.pop("password_confirm")
        inserted_data = db_model(**new_data).save()

    except ValidationError as e:
        try:
            err_ar = str(e).split("(")
            err = err_ar[2].replace(")", "")
            return False, None, err
        except:
            return False, None, str(e)

    except NotUniqueError as e:
        return False, None, str(e)

    new_data["id"] = str(inserted_data.id)
    new_data["created_at"] = inserted_data.created_at.strftime("%Y-%m-%d, %H:%M:%S")
    new_data["updated_at"] = inserted_data.updated_at.strftime("%Y-%m-%d, %H:%M:%S")

    if len(inserted_data) > 0:
        return True, inserted_data, msg
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


def get_data_by_username(db_model, username):
    try:
        data = db_model.objects.get(username=username).to_json()
    except Exception as e:
        return False, None

    dict_data = mongo_dict_to_dict(data)

    return True, dict_data


def del_data_by_id(db_model, _id):
    try:
        db_model.objects.get(id=_id).delete()
    except Exception as e:
        return False, str(e)

    return True, None


def upd_data_by_id(db_model, _id, new_data):
    try:
        pop_if_any(new_data, "password")
        pop_if_any(new_data, "created_at")
        pop_if_any(new_data, "updated_at")
        pop_if_any(new_data, "id")
        db_model.objects.get(id=_id).update(**new_data)
    except Exception as e:
        return False, None, str(e)

    new_data["id"] = _id
    new_data["updated_at"] = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")

    return True, new_data, None


def store_jwt_data(json_data):
    payload = {
        # "username": json_data["username"],
        "name": json_data["username"] + ":" + json_data["password"],  # username and pass joined by double colon
        'exp': datetime.utcnow() + timedelta(seconds=int(asab.Config["jwt"]["exp_delta_seconds"]))
    }
    access_token = jwt.encode(payload, asab.Config["jwt"]["secret_key"], algorithm=asab.Config["jwt"]["algorithm"])
    access_token_expired = jwt.decode(access_token, verify=False)["exp"]
    return access_token.decode(), access_token_expired
