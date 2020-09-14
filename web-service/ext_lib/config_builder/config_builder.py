import asab
import configparser


class ConfigBuilder:
	def __init__(self):
		self.config = configparser.ConfigParser()
		self.conf_path = None

	def set_default_redis_conf(self):
		self.config["redis"] = {
			"hostname": asab.Config["redis"]["hostname"],
			# "port": "6379",
			"password": asab.Config["redis"]["password"],
			# "db": "0"
		}

	def set_default_mongodb_conf(self):
		self.config["asab:storage"] = {
			# "type": "mongodb",
			# "mongodb_database": "eagleeyeDB",
			"mongodb_uri": "mongodb://%s:27017" % asab.Config["asab:storage"]["mongodb_host"],
			"mongodb_host": asab.Config["asab:storage"]["mongodb_host"]
		}

	def set_default_yolov3_conf(self):
		self.config["objdet:yolo"] = {
			# "output": "outputs/",
			"output": asab.Config["objdet:yolo"]["output"],
			# "source_folder_prefix": "out",
			# "file_ext": ".png",

			# "dump_raw_img": "0",
			# "dump_bbox_img": "0",
			# "dump_crop_img": "0",
			# "save_txt": "0",
			# "txt_format": "cartucho",

			# "agnostic_nms": "1",
			# "half": "0",
			# "img_size": "608",
			# "device": "",
			# "conf_thres": "0.1",

			# # It is not used
			# "iou_thres": "0.1",
			# "classes": "+",

			"names": asab.Config["objdet:yolo"]["names"],
			"cfg": asab.Config["objdet:yolo"]["cfg"],
			"weights": asab.Config["objdet:yolo"]["weights"],

			# Extra algorithms in EageleEYE
			# "candidate_selection": cand_sel,
			# "persistence_validation": pers_val,

			# "auto_restart": "1",
			# "cv_out": "1",
			# "window_size_height": "1920",
			# "window_size_width": "1080"
		}

	def set_custom_conf(self, key, items):
		self.config[key] = items

		# to convert any Boolean into String `1` or `0`
		for skey, sval in self.config[key].items():
			if isinstance(self.config[key][skey], bool):
				if self.config[key][skey]:
					self.config[key][skey] = "1"
				else:
					self.config[key][skey] = "0"

			if self.config[key][skey] == "True" or self.config[key][skey] == "False":
				if self.config[key][skey] == "True":
					self.config[key][skey] = "1"
				else:
					self.config[key][skey] = "0"

	def set_config_path(self, path):
		self.conf_path = path

	def create_config(self):
		with open(self.conf_path, 'w') as configfile:
			self.config.write(configfile)
