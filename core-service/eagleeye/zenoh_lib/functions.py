import time
import numpy as np
import logging
import cv2

###

L = logging.getLogger(__name__)


###


def extract_compressed_tagged_img(consumed_data, is_decompress=True):
	"""
		Expected data model:
		[
			[img_data],  # e.g. 1000
			[drone_id],  # extra tag 01
			[t0_part_1],  # extra tag 02
			[t0_part_2],  # extra tag 03
			[frame_id],  # extra tag 04
			[img_compr_lat_part_1],  # extra tag 05
			[img_compr_lat_part_2],  # extra tag 6
			[total_number_of_tag],
			[tagged_data_len],  # total array size: `img_data` + `total_number_of_tag` + 1
		]
	"""
	t1_zenoh_pubsub = time.time()

	t0_decode = time.time()

	decoded_data = np.frombuffer(consumed_data.payload, dtype=np.int64)
	decoded_data_len = list(decoded_data.shape)[0]
	decoded_data = decoded_data.reshape(decoded_data_len, 1)
	array_len = decoded_data[-1][0]
	extra_tag_len = decoded_data[-2][0]
	encoded_img_len = array_len - extra_tag_len

	t1_decode = (time.time() - t0_decode) * 1000
	L.warning(('[%s] Latency DECODING Payload (%.3f ms) ' % ("ZENOH CONSUMER", t1_decode)))

	# Extract information
	t0_tag_extraction = time.time()
	drone_id = extract_drone_id(decoded_data, encoded_img_len)
	t0_zenoh_pubsub = extract_t0(decoded_data, encoded_img_len)
	frame_id = extract_frame_id(decoded_data, encoded_img_len)
	img_compr_lat = extract_img_compr_lat(decoded_data, encoded_img_len)
	t1_tag_extraction = (time.time() - t0_tag_extraction) * 1000
	L.warning(('[%s] Latency Tag Extraction (%.3f ms) ' % ("ZENOH CONSUMER", t1_tag_extraction)))

	# calculate zenoh pubsub
	zenoh_pubsub_latency = (t1_zenoh_pubsub - t0_zenoh_pubsub) * 1000
	L.warning(('[%s][Frame-{}] Latency Zenoh Comm. PubSub (%.3f ms) '.format(frame_id) % ("ZENOH CONSUMER",
																						  zenoh_pubsub_latency)))

	# popping tagged information
	t0_non_img_cleaning = time.time()
	for i in range(extra_tag_len):
		decoded_data = np.delete(decoded_data, -1)
	decoded_data = decoded_data.reshape(decoded_data_len - extra_tag_len, 1)

	t1_non_img_cleaning = (time.time() - t0_non_img_cleaning) * 1000
	L.warning(
		('[%s] Latency Non Image Cleaning (%.3f ms) ' % ("ZENOH CONSUMER", t1_non_img_cleaning)))

	# extracting (compressed) image information
	t0_img_extraction = time.time()
	extracted_cimg = decoded_data[:-1].copy().astype('uint8')
	t1_img_extraction = (time.time() - t0_img_extraction) * 1000
	L.warning(('[%s] Latency Image Extraction (%.3f ms) ' % ("ZENOH CONSUMER", t1_img_extraction)))

	# Image de-compression (restore back into FullHD)
	t0_decompress_img = time.time()
	if is_decompress:
		deimg_len = list(extracted_cimg.shape)[0]
		decoded_img = extracted_cimg.reshape(deimg_len, 1)
		decompressed_img = cv2.imdecode(decoded_img, 1)  # decompress

	# pending the process to de-compress the image
	else:
		decompressed_img = extracted_cimg
	t1_decompress_img = (time.time() - t0_decompress_img) * 1000
	L.warning(('[%s] Latency DE-COMPRESSING IMG (%.3f ms)' % ("ZENOH CONSUMER", t1_decompress_img)))
	L.warning(('[%s] Latency COMPRESSING IMG (%.3f ms)' % ("ZENOH CONSUMER", img_compr_lat)))

	# cv2.imwrite("decompressed_img.jpg", decompressed_img)
	# cv2.imwrite("decompressed_img_{}.jpg".format(str(t0_decompress_img)), decompressed_img)

	# latency data
	latency_data = {
		"decoding_payload": t1_decode,
		"clean_decoded_payload": t1_non_img_cleaning,
		"extract_img_data": t1_img_extraction,
		"decompress_img": t1_decompress_img,
		"zenoh_pubsub": zenoh_pubsub_latency,
		"compress_img": img_compr_lat,
	}

	# decode data
	img_info = {
		"id": drone_id,
		"img": decompressed_img,
		"timestamp": t0_zenoh_pubsub,
		"frame_id": frame_id,
	}

	return img_info, latency_data


def encrypt_str(str_val, byteorder="little"):
	encrypted_bytes = str_val.encode('utf-8')
	encrypted_val = int.from_bytes(encrypted_bytes, byteorder)  # `byteorder` must be either 'little' or 'big'
	return encrypted_val  # max 19 digit


def decrypt_str(int_val, byteorder="little"):
	decrypted_bytes = int_val.to_bytes((int_val.bit_length() + 7) // 8, byteorder)  # byteorder must be either 'little' or 'big'
	decrypted_str = decrypted_bytes.decode('utf-8')
	return decrypted_str


def extract_drone_id(data, img_len):
	drone_idx = img_len
	return decrypt_str(int(data[drone_idx][0]))


def extract_t0(data, img_len):
	""" Extract timestamp (t0) captured by Zenoh's Consumer """
	t0_p1_idx = img_len + 1
	t0_p2_idx = img_len + 2

	t0 = "{}.{}".format(
		data[t0_p1_idx][0],
		data[t0_p2_idx][0],
	)
	return float(t0)


def extract_img_compr_lat(data, img_len):
	""" Extract Img compression latency captured by Zenoh's Consumer """
	lat_idx_0 = img_len + 4
	lat_idx_1 = img_len + 5

	compr_lat = "{}.{}".format(
		data[lat_idx_0][0],
		data[lat_idx_1][0],
	)
	return float(compr_lat)


def extract_frame_id(data, img_len):
	""" Extract drone_id captured by Zenoh's Consumer """
	frame_idx = img_len + 3
	return decrypt_str(int(data[frame_idx][0]))
