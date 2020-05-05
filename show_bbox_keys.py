from libs.addons.redis.my_redis import MyRedis

redis = MyRedis()
print(" Current Keys = ", redis.rc_bbox.keys())
