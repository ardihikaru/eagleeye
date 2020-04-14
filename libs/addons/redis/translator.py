import simplejson as json
import time
import cv2

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

def frame_producer(my_redis, frame_id, ret, frame, save_path, channel, rc_latency=None, drone_id=None):
    if ret:
        # Save image
        # print("###### save_path = ", save_path)
        t0_save2disk = time.time()
        cv2.imwrite(save_path, frame)
        t_save2disk = time.time() - t0_save2disk
        # print(".. image is saved in (%.3fs)" % (time.time() - t0_save2disk))

        # Latency: save frame into disk
        t_f2disk_key = "f2disk-" + str(drone_id) + "-" + str(frame_id)
        print('\nLatency [Save to disk] of frame-%d: (%.5fs)' % (frame_id, t_save2disk))
        redis_set(rc_latency, t_f2disk_key, t_save2disk)

        # Publish information
        t0_pub2frame = time.time()
        data = {
            "frame_id": frame_id,
            "img_path": save_path
        }
        p_mdata = json.dumps(data)
        # print(" .. Start publishing")
        # my_redis.publish('stream', p_mdata)
        my_redis.publish(channel, p_mdata)
        t_pub2frame = time.time() - t0_pub2frame
        # print(".. frame is published in (%.3fs)" % (time.time() - t0))

        # Latency: capture publish frame information
        print('\nLatency [Publish frame info] of frame-%s: (%.5fs)' % (str(frame_id), t_pub2frame))
        t_pub2frame_key = "pub2frame-" + str(drone_id) + "-" + str(frame_id)
        redis_set(rc_latency, t_pub2frame_key, t_pub2frame)
