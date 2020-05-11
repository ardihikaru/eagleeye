from libs.addons.redis.translator import redis_set, redis_get
import simplejson as json
import time


def store_latency(rc, key, val, is_json=False):
    if is_json:
        val = json.dumps(val)
    redis_set(rc, key, val)

def store_fps(rc, key, drone_id, total_frames=None, t0=None):
    if t0 is None:
        t_elapsed = time.time() - get_t0_video(rc, drone_id)
    else:
        t_elapsed = time.time() - t0

    if total_frames is None:  # `None` means it calculates the FPS of each YOLO worker
        total_frames = get_total_captured_frames(rc, drone_id)
    time_per_frame = total_frames / t_elapsed
    # current_fps = 1000 / time_per_frame
    current_fps = 1.0 / time_per_frame
    current_fps = round(current_fps, 2)
    redis_set(rc, key, current_fps)

    return total_frames, current_fps

def get_t0_video(rc, drone_id):
    t_start_key = "start-" + str(drone_id)
    return redis_get(rc, t_start_key)

def get_total_captured_frames(rc, drone_id):
    t_total_frames_key = "total-frames-" + str(drone_id)
    total_frames = redis_get(rc, t_total_frames_key)
    return total_frames
