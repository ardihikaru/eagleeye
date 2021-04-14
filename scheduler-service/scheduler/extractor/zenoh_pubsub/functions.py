import time
import numpy as np


def extract_compressed_tagged_img(consumed_data):
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
	# decode payload
	t0_decode = time.time()
	decoded_data = decode_payload(consumed_data.payload)
	extra_tag_len, encoded_img_len = extract_decoded_payload(decoded_data)
	t1_decode = (time.time() - t0_decode) * 1000
	L.warning(('[%s] Latency DECODING Payload (%.3f ms) ' % ("ZENOH CONSUMER", t1_decode)))

	# Extract information
	t0_tag_extraction = time.time()
	drone_id = extract_drone_id(decoded_data, encoded_img_len)
	t0 = extract_t0(decoded_data, encoded_img_len)
	t1_tag_extraction = (time.time() - t0_tag_extraction) * 1000
	L.warning(('[%s] Latency Tag Extraction (%.3f ms) ' % ("ZENOH CONSUMER", t1_tag_extraction)))

	# popping tagged information
	t0_non_img_cleaning = time.time()
	for i in range(extra_tag_len):
		decoded_data = np.delete(decoded_data, -1)
	decoded_data = decoded_data.reshape(decoded_data_len - 5, 1)
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
	# print(" ### SHAPE: decoded_img = ", decoded_img.shape)
	deimg_len = list(extracted_cimg.shape)[0]
	# print(" ----- deimg_len:", deimg_len)
	decoded_img = extracted_cimg.reshape(deimg_len, 1)
	# print(" ### SHAPE: decoded_img = ", decoded_img.shape, type(decoded_img), type(decoded_img[0][0]))
	decompressed_img = cv2.imdecode(decoded_img, 1)  # decompress
	# print(" ----- SHAPE decompressed_img:", decompressed_img.shape)
	t1_decompress_img = (time.time() - t0_decompress_img) * 1000
	L.warning(('[%s] Latency DE-COMPRESSING IMG (%.3f ms) \n' % ("ZENOH CONSUMER", t1_decompress_img)))

	# cv2.imwrite("decompressed_img.jpg", decompressed_img)
	# cv2.imwrite("decompressed_img_{}.jpg".format(str(t0_decompress_img)), decompressed_img)

	# decode data
	img_info = {
		"id": drone_id,
		"img": decompressed_img,
		"timestamp": t0,
	}

	return img_info


def decode_payload(payload):
	decoded_payload = np.frombuffer(payload, dtype=np.int64)
	decoded_payload_len = list(decoded_payload.shape)[0]
	decoded_payload = decoded_payload.reshape(decoded_payload_len, 1)

	return decoded_payload


def extract_decoded_payload(decoded_payload):
	array_len = decoded_data[-1][0]
	extra_tag_len = decoded_data[-2][0]
	encoded_img_len = array_len - extra_tag_len

	return extra_tag_len, encoded_img_len


def extract_drone_id(data, img_len):
	""" Extract drone_id captured by Zenoh's Consumer """
	drone_idx = img_len
	return decrypt_str(int(data[drone_idx][0]))


def extract_t0(data, img_len):
	""" Extract timestamp (t0) captured by Zenoh's Consumer """
	to_p1_idx = img_len + 2
	to_p2_idx = img_len + 3

	t0 = "{}.{}".format(
		data[to_p1_idx][0],
		data[to_p2_idx][0],
	)
	return float(t0)
