from kafka import KafkaProducer
import numpy as np
import cv2

producer = KafkaProducer(bootstrap_servers='localhost:9092')

topic = "email_request_pool"
# topic = "image_pool"

# define value for image
root_path = "/home/s010132/devel/eagleeye/data/out1.png"
value = cv2.imread(root_path)
value = value.tobytes()

# producer.send(topic, b"kucing")
producer.send(topic, value)
producer.close()
