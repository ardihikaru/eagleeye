import configparser


class ConfigBuilder:
	def __init__(self):
		self.config = configparser.ConfigParser()
		self.conf_path = None

	def set_default_redis_conf(self):
		self.config["redis"] = {
			"hostname": "localhost",
			"port": "6379",
			"password": "bismillah",
			"db": "0"
		}

	def set_default_mongodb_conf(self):
		self.config["asab:storage"] = {
			"type": "mongodb",
			"mongodb_database": "eagleeyeDB",
			"mongodb_uri": "mongodb://localhost:27017"
		}

	def set_default_pubsub_channel_conf(self, node_id=""):
		self.config["pubsub:channel"] = {
			"scheduler": "scheduler",
			"node": "node-"+node_id,
			"mongodb_uri": "mongodb://localhost:27017"
		}

	# def set_default_yolov3_conf(self, cand_sel=False, pers_val=False):
	def set_default_yolov3_conf(self):
		# if cand_sel:
		# 	cand_sel = "1"
		# else:
		# 	cand_sel = "0"
		# if pers_val:
		# 	pers_val = "1"
		# else:
		# 	pers_val = "0"
		self.config["objdet:yolo"] = {
			"output": "outputs/",
			"source_folder_prefix": "out",
			"file_ext": ".png",

			"dump_raw_img": "0",
			"dump_bbox_img": "0",
			"dump_crop_img": "0",
			"save_txt": "0",
			"txt_format": "cartucho",

			"agnostic_nms": "1",
			"half": "0",
			"img_size": "416",
			"device": "",
			"conf_thres": "0.1",
			"iou_thres": "0.1",
			# "classes": "+",
			"names": "../object-detection-service/config_files/yolo/data/coco.names",
			"cfg": "../object-detection-service/config_files/yolo/cfg/yolov3.cfg",
			"weights": "../object-detection-service/config_files/yolo/weights/yolov3.weights",

			# Extra algorithms in EageleEYE
			# "candidate_selection": cand_sel,
			# "persistence_validation": pers_val,

			"auto_restart": "1",
			"cv_out": "1",
			"window_size_height": "1920",
			"window_size_width": "1080"
		}

	def set_custom_conf(self, key, items):
		self.config[key] = items

		# to convert any Boolean into String `1` or `0`
		for skey, sval in self.config[key].items():
			print(" >>> self.config[key][skey] :", self.config[key][skey], type(self.config[key][skey]))
			if isinstance(self.config[key][skey], bool):
				if self.config[key][skey]:
					print(" >>> PERBARUI value coi")
					self.config[key][skey] = "1"
				else:
					self.config[key][skey] = "0"

			if self.config[key][skey] == "True" or self.config[key][skey] == "False":
				if self.config[key][skey] == "True":
					self.config[key][skey] = "1"
				else:
					self.config[key][skey] = "0"
			print(">>> NEW VAL: ", self.config[key][skey])

	def set_config_path(self, path):
		self.conf_path = path

	def create_config(self):
		with open(self.conf_path, 'w') as configfile:
			self.config.write(configfile)
