import ntplib  # pip install ntplib
from datetime import datetime, timezone

# NTP_SERVERS = ['140.113.86.92']  # IP Docker Container
NTP_SERVERS = ['localhost']  # IP Docker Container

for server in NTP_SERVERS:
	client = ntplib.NTPClient()
	response = client.request(server, version=3)
	print(f"server: {server}")
	print(f"client time of request: {datetime.fromtimestamp(response.orig_time, timezone.utc)}")
	print(f"server responded with: {datetime.fromtimestamp(response.tx_time, timezone.utc)}")
