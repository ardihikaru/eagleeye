from redis import StrictRedis
import json
import time

HOST = "localhost"
PORT = 6379
DB = 0
CHANNEL = "node-5f683910619c2e18f1609b73"

rc = StrictRedis(
    host=HOST,
    port=PORT,
    db=DB,
    decode_responses=True
)


def pub(my_redis, channel, message):
    my_redis.publish(channel, message)


dump_request = json.dumps({"active": False})

while True:
    print("> Publishing data")
    pub(rc, CHANNEL, dump_request)
    time.sleep(1)
