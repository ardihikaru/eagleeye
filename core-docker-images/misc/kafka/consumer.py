from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                                 # auto_offset_reset='earliest',
                                 # auto_offset_reset='latest',
                                 consumer_timeout_ms=1000)

topic = "email_request_pool"
consumer.subscribe([topic])

while True:
	for message in consumer:
		print(" --- DISINI .. message.value)= ", message.value)
		# email_request = json.loads(message.value)
		# print(email_request)
		print()

# consumer.close()
