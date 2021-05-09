from zenoh_lib.zenoh_net_subscriber import ZenohNetSubscriber
import sys
import cv2
import time
from datetime import datetime
import logging
import numpy as np

###

L = logging.getLogger(__name__)


###


def decrypt_str(int_val, byteorder="little"):
	decrypted_bytes = int_val.to_bytes((int_val.bit_length() + 7) // 8, byteorder)  # byteorder must be either 'little' or 'big'
	decrypted_str = decrypted_bytes.decode('utf-8')
	return decrypted_str


def extract_drone_id(data, img_len):
	drone_idx = img_len
	return decrypt_str(int(data[drone_idx][0]))


def extract_t0(data, img_len):
	to_p1_idx = img_len + 2
	to_p2_idx = img_len + 3

	t0 = "{}.{}".format(
		data[to_p1_idx][0],
		data[to_p2_idx][0],
	)
	return float(t0)


def listener_v2(consumed_data):
	"""
	Expected data model:
	[
		[img_data],  # e.g. 1000
		[drone_id],  # extra tag 01
		[t0_part_1],  # extra tag 02
		[t0_part_2],  # extra tag 03
		[total_number_of_tag],
		[tagged_data_len],  # total array size: `img_data` + `total_number_of_tag` + 1
	]
	"""
	print(" #### LISTENER ..")

	t0_decode = time.time()
	decoded_data = np.frombuffer(consumed_data.payload, dtype=np.int64)
	decoded_data_len = list(decoded_data.shape)[0]
	decoded_data = decoded_data.reshape(decoded_data_len, 1)
	array_len = decoded_data[-1][0]
	extra_tag_len = decoded_data[-2][0]
	encoded_img_len = array_len - extra_tag_len
	# print(" ----- decoded_data_len:", decoded_data_len)
	# print(" ----- array_len:", array_len)
	# print(" ----- extra_tag_len:", extra_tag_len)
	# print(" ----- encoded_img_len:", encoded_img_len)
	# print(" ----- SHAPE decoded_data:", decoded_data.shape)
	# decoded_data = np.frombuffer(encoded_data, dtype=np.uint64)
	# print(type(decoded_data), decoded_data.shape)
	# print(type(decoded_data))
	# print(" TAGGED DATA LEN:", decoded_data[:-1])
	# print(decoded_data)
	t1_decode = (time.time() - t0_decode) * 1000
	print(('[%s] Latency DECODING Payload (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_decode)))

	# test printing
	# print(" ##### decoded_data[-1][0] (tagged_data_len) = ", decoded_data[-1][0])  # tagged_data_len
	# print(" ##### decoded_data[-2][0] (total_number_of_tag) = ", decoded_data[-2][0])  # total_number_of_tag
	# print(" ##### decoded_data[-3][0] (t0_part_2) = ", decoded_data[-3][0])  # t0_part_2
	# print(" ##### decoded_data[-4][0] (t0_part_1) = ", decoded_data[-4][0])  # t0_part_1
	# print(" ##### decoded_data[-5][0] (drone_id) = ", decoded_data[-5][0])  # drone_id
	# print(" ##### decoded_data[-6][0] (img_data) = ", decoded_data[-6][0])  # img_data

	# Extract information
	t0_tag_extraction = time.time()
	drone_id = extract_drone_id(decoded_data, encoded_img_len)
	t0 = extract_t0(decoded_data, encoded_img_len)
	# print(" ----- drone_id:", drone_id, type(drone_id))
	# print(" ----- t0:", t0, type(t0))
	t1_tag_extraction = (time.time() - t0_tag_extraction) * 1000
	print(('[%s] Latency Tag Extraction (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_tag_extraction)))

	# popping tagged information
	t0_non_img_cleaning = time.time()
	# print(" ----- OLD SHAPE decoded_data:", decoded_data.shape)
	for i in range(extra_tag_len):
		decoded_data = np.delete(decoded_data, -1)
	decoded_data = decoded_data.reshape(decoded_data_len-5, 1)
	# print(" ----- NEWWWW SHAPE decoded_data:", decoded_data.shape)
	# print(" ##### decoded_data[-1][0] = ", decoded_data[-1][0])  # tagged_data_len
	t1_non_img_cleaning = (time.time() - t0_non_img_cleaning) * 1000
	print(('[%s] Latency Non Image Cleaning (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_non_img_cleaning)))

	# extracting (compressed) image information
	t0_img_extraction = time.time()
	extracted_cimg = decoded_data[:-1].copy().astype('uint8')
	t1_img_extraction = (time.time() - t0_img_extraction) * 1000
	print(('[%s] Latency Image Extraction (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_img_extraction)))

	# Image de-compression (restore back into FullHD)
	t0_decompress_img = time.time()
	# print(" ### SHAPE: decoded_img = ", decoded_img.shape)
	deimg_len = list(extracted_cimg.shape)[0]
	# print(" ----- deimg_len:", deimg_len)
	decoded_img = extracted_cimg.reshape(deimg_len, 1)
	# print(" ### SHAPE: decoded_img = ", decoded_img.shape, type(decoded_img), type(decoded_img[0][0]))
	decompressed_img = cv2.imdecode(decoded_img, 1)  # decompress
	# print(" ----- SHAPE decompressed_img:", decompressed_img.shape)
	t1_decompress_img = (time.time() - t0_decompress_img) * 1000
	print(('[%s] Latency DE-COMPRESSING IMG (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_decompress_img)))

	# cv2.imwrite("decompressed_img.jpg", decompressed_img)
	# cv2.imwrite("decompressed_img_{}.jpg".format(str(t0_decompress_img)), decompressed_img)

# # Scenario 1: Simple Pub/Sub with a single PC
# selector = "/demo/**"

# Scenario 2: Pub/Sub with two hosts
"""
	Simulated scenario:
	- `Host #01` will has IP `192.168.1.110`
	- `Host #01` run `subscriber`
	- `Host #02` run `publisher`
	- Asumming that both hosts are in the multicast network environment
"""
selector = "/eagleeye/svc/**"
# listener = "tcp/140.113.86.92:7446"
listener = "tcp/localhost:7446"

sub = ZenohNetSubscriber(
	_selector=selector, _session_type="SUBSCRIBER", _listener=listener
)
sub.init_connection()

# sub.register()
sub.register(listener_v2)
# subscriber = sub.get_subscriber()
subscriber = sub.get_subscriber()
L.warning("[ZENOH] Press q to stop...")
c = '\0'
while c != 'q':
	c = sys.stdin.read(1)

# # closing Zenoh subscription & session
sub.close_connection(subscriber)
