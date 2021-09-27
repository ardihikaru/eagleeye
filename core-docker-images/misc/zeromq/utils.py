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


def get_img_fsize_in_float(img_bytes):
	img_size_raw = humanbytes(img_bytes)
	img_size_arr = img_size_raw.split(" ")
	img_size_val = float(img_size_arr[0])
	ext_txt = img_size_arr[1]

	# make sure to use the same measurement
	if ext_txt == "KB":
		img_size_val /= 1000
		ext_txt = "MB"

	return img_size_val, ext_txt
