from libs.addons.redis.my_redis import MyRedis

redis = MyRedis()
redis.delete_all_keys()