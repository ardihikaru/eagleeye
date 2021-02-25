import simplejson as json


def str_encryptor(val):
	"""
	Encrypt string into integer
	"""
	return int.from_bytes(val.encode('utf-8'), byteorder='big')


def str_decryptor(val):
	"""
	Encrypt string into integer
	"""
	return int.to_bytes(val, length=len(strg), byteorder='big').decode('utf-8')
