import time
# from datetime import datetime
import ntplib  # pip install ntplib
from datetime import datetime, timezone

server = "192.168.1.10"

while True:
	rtc = time.clock_gettime(time.CLOCK_REALTIME)
	dt_object = datetime.fromtimestamp(rtc)

	# t0_get_ntp_time = time.time()
	# # ntp server
	# client = ntplib.NTPClient()
	# response = client.request(server, version=3)
	# # print(f"server: {server}")
	# client_time_req = datetime.fromtimestamp(response.orig_time, timezone.utc)
	# server_time_resp = datetime.fromtimestamp(response.tx_time, timezone.utc)
	# # time_diff = (server_time_resp - client_time_req).total_seconds()
	# print("{}".format(server_time_resp))
	# t1_get_ntp_time = (time.time() - t0_get_ntp_time) * 1000
	# print(" ## Time to get NTP: (%.2f ms)" % t1_get_ntp_time)
	# # print(f"client time of request: {client_time_req}, {type(client_time_req)}")
	# # print(f"server responded with: {server_time_resp}, {type(server_time_resp)}")
	# # print(" ## TOTAL DIFF: ", time_diff)

	# print("System RTC = {}".format(rtc))
	# print("System Datetime (RTC) = {}\n".format(dt_object))
	print("{}".format(dt_object))
	time.sleep(1)
