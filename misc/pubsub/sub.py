from redis import StrictRedis
import json

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


def pubsub_to_json(json_data):
	data = None
	try:
		data = json.loads(json_data)
	except:
		pass
	return data


consumer = rc.pubsub()
consumer.subscribe([CHANNEL])
for item in consumer.listen():
	if isinstance(item["data"], int):
		print("> Lewati")
	else:
		info = pubsub_to_json(item["data"])
		print(info)
