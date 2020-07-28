import aiohttp
from ext_lib.utils import get_json_template
from ext_lib.redis.translator import redis_set
import logging

###

L = logging.getLogger(__name__)

###


def validate_request_json(request_json):
	valid_list = ["raw", "algorithm", "uri", "exec", "worker"]
	if not isinstance(request_json, dict):
		raise aiohttp.web.HTTPBadRequest()

	for key in valid_list:
		if key not in request_json:
			# Log the error
			L.error("Invalid request: {}".format("key `%s` not found." % key))
			raise aiohttp.web.HTTPBadRequest()


def request_to_redisdb(rc, request_json):
	for key, value in request_json.items():
		redis_set(rc, key, value)
