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

	def set_default_yolov3_conf(self, node_id=""):
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

			"auto_restart": "1",
			"cv_out": "1",
			"window_size_height": "1920",
			"window_size_width": "1080"
		}

	def set_custom_conf(self, key, items):
		self.config[key] = items

	def set_config_path(self, path):
		self.conf_path = path

	def create_config(self):
		with open(self.conf_path, 'w') as configfile:
			self.config.write(configfile)
