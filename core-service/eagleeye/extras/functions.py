from datetime import datetime
from os import path
import os


def get_current_datetime(is_folder=False):
	if is_folder:
		return datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
	else:
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_datetime_ms(is_folder=False):
	if is_folder:
		return datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
	else:
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


def create_folder(target_path):
	if not path.exists(target_path):
		os.mkdir(target_path)


def is_img_exist(target_path):
	if path.exists(target_path):
		return True
	else:
		return False


def encrypt_str(str_val, byteorder="little"):
	""" Converts a string value into an integer value """
	encrypted_bytes = str_val.encode('utf-8')
	encrypted_val = int.from_bytes(encrypted_bytes, byteorder)  # `byteorder` must be either 'little' or 'big'
	return encrypted_val  # max 19 digit


def decrypt_str(int_val, byteorder="little"):
	""" Converts an integer value into a string value """
	decrypted_bytes = int_val.to_bytes((int_val.bit_length() + 7) // 8, byteorder)  # byteorder must be either 'little' or 'big'
	decrypted_str = decrypted_bytes.decode('utf-8')
	return decrypted_str


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


def humanbytes(B):
	""" Return the given bytes as a human friendly KB, MB, GB, or TB string """
	B = float(B)
	KB = float(1024)
	MB = float(KB ** 2)  # 1,048,576
	GB = float(KB ** 3)  # 1,073,741,824
	TB = float(KB ** 4)  # 1,099,511,627,776

	if B < KB:
		return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
	elif KB <= B < MB:
		return '{0:.2f} KB'.format(B/KB)
	elif MB <= B < GB:
		return '{0:.2f} MB'.format(B/MB)
	elif GB <= B < TB:
		return '{0:.2f} GB'.format(B/GB)
	elif TB <= B:
		return '{0:.2f} TB'.format(B/TB)
