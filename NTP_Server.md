# NTP Server
Provided by cturra: [https://hub.docker.com/r/cturra/ntp ]()
## How to run
	$ docker pull cturra/ntp
	$ docker run --name=ntp            \
	              --restart=always      \
	              --detach              \
	              --publish=123:123/udp \
				  --env=NTP_SERVERS="0.tw.pool.ntp.org,1.tw.pool.ntp.org,2.tw.pool.ntp.org,3.tw.pool.ntp.org"\
	              cturra/ntp
## Check NTP container status
	$ docker exec ntp chronyc tracking
## How to query time from NTP server
1. Via terminal command
		$ ntpdate -q <DOCKER_HOST_IP>
2. Via python script
		# Author: https://stackoverflow.com/a/31256302
		
		import ntplib
		from datetime import datetime, timezone
		
		NTP_SERVERS = ['140.113.86.92'] # IP Docker Container
		
		for server in NTP_SERVERS:
			client = ntplib.NTPClient()
			response = client.request(server, version=3)
			print(f"server: {server}")
			print(f"client time of request: {datetime.fromtimestamp(response.orig_time, timezone.utc)}")
			print(f"server responded with: {datetime.fromtimestamp(response.tx_time, timezone.utc)}")

