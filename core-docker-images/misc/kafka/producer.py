# import asab
# from time import sleep
# from json import dumps
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092')

topic = "email_request_pool"

producer.send(topic, b"kucing")
producer.close()
