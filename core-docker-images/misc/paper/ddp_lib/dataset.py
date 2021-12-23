import csv


class Dataset(object):
	# define variable name
	FRAME_ID = "frame_id"
	ORIG_IMG_SIZE_MBYTES = "orig_img_size_mbytes"
	ENCODED_IMG_SIZE_MBYTES = "encoded_img_size_mbytes"
	ENCODED_IMG_SIZE_MBITS = "encoded_img_size_mbits"

	def __init__(self, dataset_path):
		self.dataset = []
		self.dataset_path = dataset_path

	def load_dataset(self):
		with open(self.dataset_path, newline='') as csvfile:
			# Separate fields with colons, read the contents of the file
			rows = csv.reader(csvfile, delimiter=',')

			for row in rows:
				# reformat
				row = [int(row[i]) if i == 0 else float(row[i]) for i in range(len(row))]
				self.dataset.append({
					self.FRAME_ID: row[0],
					self.ORIG_IMG_SIZE_MBYTES: row[1],
					self.ENCODED_IMG_SIZE_MBYTES: row[2],
					self.ENCODED_IMG_SIZE_MBITS: row[3],
				})

	def get_dataset(self):
		return self.dataset
