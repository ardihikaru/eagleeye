import ntplib  # pip install ntplib
from datetime import datetime, timezone

# NTP_SERVERS = ['140.113.86.92']  # IP Docker Container
# NTP_SERVERS = ['localhost']  # IP Docker Container
NTP_SERVERS = ['192.168.1.10']  # IP Docker Container

for server in NTP_SERVERS:
	client = ntplib.NTPClient()
	response = client.request(server, version=3)
	print(f"server: {server}")
	client_time_req = datetime.fromtimestamp(response.orig_time, timezone.utc)
	server_time_resp = datetime.fromtimestamp(response.tx_time, timezone.utc)
	time_diff = (server_time_resp-client_time_req).total_seconds()
	print(f"client time of request: {client_time_req}, {type(client_time_req)}")
	print(f"server responded with: {server_time_resp}, {type(server_time_resp)}")
	print(" ## TOTAL DIFF: ", time_diff)

print(" --- DONE --- ")
