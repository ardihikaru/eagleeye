from pymongo import MongoClient
from enum import Enum
import asyncio
import csv


CSV_FILE_PATH = "./latency.csv"

# field name of Latency collection
FN_FRAME_ID = "frame_id"
FN_CATEGORY = "category"
FN_ALGORITHM = "algorithm"
FN_SECTION = "section"
FN_LATENCY = "latency"
FN_NODE_ID = "node_id"
FN_NODE_NAME = "node_name"


async def load_latency_data(latency_data):
	# load data from database and fill in the empty array
	with MongoClient() as client:
		db = client.eagleeyeDB
		for doc in db.Latency.find():
			latency_data.append([
				doc.get(FN_FRAME_ID, "-"),
				doc.get(FN_CATEGORY, "-"),
				doc.get(FN_ALGORITHM, "-"),
				doc.get(FN_SECTION, "-"),
				doc.get(FN_LATENCY, "-"),
				doc.get(FN_NODE_ID, "-"),
				doc.get(FN_NODE_NAME, "-"),
			])

	return latency_data


async def write_to_csv_file(file_path, latency_header, latency_data):
	print("> Start to write data to file `{}`".format(file_path))
	print("> Total collected latency data is `{}` records".format(len(latency_data)))
	# write to CSV file
	# # open the file in the write mode
	with open(file_path, 'w', encoding='UTF8', newline='') as f:
		# create the csv writer
		writer = csv.writer(f)

		# write the header
		writer.writerow(latency_header)

		# write a row to the csv file
		writer.writerows(latency_data)
	print("> All records have been successfully exported to the CSV file!")
	exit()


async def main():
	# create an empty array to store into the CSV file
	latency_header = [FN_FRAME_ID, FN_CATEGORY, FN_ALGORITHM, FN_SECTION, FN_LATENCY, FN_NODE_ID, FN_NODE_NAME]
	latency_data = []  # to collect all latency

	# load latency and assign to an empty var
	latency_data = await load_latency_data(latency_data)

	# write to CSV file
	await write_to_csv_file(CSV_FILE_PATH, latency_header, latency_data)

if __name__ == '__main__':
	try:
		asyncio.get_event_loop().run_until_complete(main())
		asyncio.get_event_loop().run_forever()
	except Exception as e:
		print("Unable to run exporter ({})".format(e))
	except KeyboardInterrupt as e:
		print("Interrupted by keyboard")
	finally:
		print("Exiting Exporter")
