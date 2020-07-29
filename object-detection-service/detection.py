from detection.app import ObjectDetectionService
# import argparse

if __name__ == '__main__':
	# parser = argparse.ArgumentParser()
	# parser.add_argument('--node', type=int, default=1, help="Node ID")

	# opt = parser.parse_args()
	# print(opt)

	# app = ObjectDetectionService(opt)
	app = ObjectDetectionService()
	app.run()
