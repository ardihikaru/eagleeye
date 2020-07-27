"""
   This file helps the system to manage and control the in-out request related to JWT protocol.
   I use and modified my own code from here:
        https://github.com/ardihikaru/flask-api/tree/master/app/addons/database_blacklist
"""

from ext_lib.redis.translator import redis_set, redis_get
import jwt


def revoke_current_token(rc, config, encoded_token):
    """
        A revoked access_token is verified by adding it into the RedisDB with added an expiration time.
            Each revoked access_token is considered as blacklisted one.
            Data in the RedisDB will be automatically deleted once it's expired
        Input:
            - access_token (From the input request)
            - exp_delta_seconds (From the app.conf)
        Process:
            - a saved key-value data in the RedisDB to
                - key = access_token; value = access_token; expiration time = exp_delta_seconds
        Return:
            a dictionary of response data:
            {
                "message": String,
                "resp_code": Integer
            }
    """
    result = {"message": None, "resp_code": 400}
    decoded_token = jwt.decode(encoded_token, verify=False)
    redis_set(rc, encoded_token.decode(), decoded_token, config["jwt"]["exp_delta_seconds"])
    result["message"] = "Token revoked"
    result["resp_code"] = 200

    return result


def is_token_revoked(rc, decoded_token):
    """
        Checks if the given token is revoked or not. Because we are adding all the
        tokens that we create into this database, if the token is present
        in the database we are going to consider it revoked (blacklisted).
        Input:
            - access_token (From the input request)
        Return:
            True or False
    """
    data = redis_get(rc, decoded_token.encode())
    if data is None:
        return False
    else:
        return True

