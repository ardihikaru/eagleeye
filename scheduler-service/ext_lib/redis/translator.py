import simplejson as json


# default = dumped kabeh.
def redis_set(redis_client, key, value, expired=None):
    value = json.dumps(value)

    if expired is not None:
        option = [value, expired]
        redis_client.set(key, *option)
    else:
        redis_client.set(key, value)


def redis_get(redis_client, key):
    data = None
    try:
        data = json.loads(redis_client.get(key))
    except:
        pass
    finally:
        return data


def redis_get_all_keys(redis_client):
    data = None
    try:
        data = json.loads(redis_client.keys())
    except:
        pass
    finally:
        return data


def pub(my_redis, channel, message):
    my_redis.publish(channel, message)


def sub(my_redis, channel, func, consumer_name=None):
    pubsub = my_redis.pubsub()
    pubsub.subscribe([channel])
    for item in pubsub.listen():
        func(consumer_name, item['data'])

