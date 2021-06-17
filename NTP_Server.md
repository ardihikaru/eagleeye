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

- MISC:
    - Condition where a host machine is **NOT** sync'd with any NTP Server yet:
      ``` 
      $ timedatectl status
                              Local time: Thu 2021-06-17 07:40:40 UTC
                          Universal time: Thu 2021-06-17 07:40:40 UTC
                                RTC time: Thu 2021-06-17 07:40:40
                               Time zone: Etc/UTC (UTC, +0000)
               System clock synchronized: yes
        systemd-timesyncd.service active: yes
                         RTC in local TZ: no  
      ```
    - Condition where a host machine is **HAS BEEN** sync'd with any NTP Server:
      ``` 
      $ timedatectl status                                                                                                  ^(*feature/integrated-ntp-server+942) 15:38:46 
                       Local time: Thu 2021-06-17 15:41:18 CST
                   Universal time: Thu 2021-06-17 07:41:18 UTC
                         RTC time: Thu 2021-06-17 07:41:18    
                        Time zone: Asia/Taipei (CST, +0800)   
        System clock synchronized: yes                                     
                      NTP service: active                       <<--- this one
                  RTC in local TZ: no
      ```
  - Check NTP container status
    ``` 
    $ docker exec ntp chronyc tracking
        Reference ID    : B7B148CA (t2.time.tw1.yahoo.com)
        Stratum         : 3
        Ref time (UTC)  : Thu Jun 17 08:17:33 2021
        System time     : 0.000875258 seconds slow of NTP time
        Last offset     : +0.000056188 seconds
        RMS offset      : 0.000056188 seconds
        Frequency       : 3.368 ppm slow
        Residual freq   : -0.000 ppm
        Skew            : 752.271 ppm
        Root delay      : 0.003868186 seconds
        Root dispersion : 0.013815410 seconds
        Update interval : 1.3 seconds
        Leap status     : Normal
    ```
    - Check query time a host machine to the specific NTP Server's IP:
        `$ ntpdate -q 172.17.0.2`
         - In this example, LB is calling container-based NTP Server (`172.17.0.2`)
    - Turn off system's NTP sync: `$ timedatectl set-ntp off`
    - Then, set this Host Machine to sync with its container-based NTP Server
        `$ sudo ntpdate -u 172.17.0.2`
    - How to check NTP's Docker container IP: 
        `$ docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container_name_or_id`
        - In this case, we use name `ntp`, so we can run:
        `$ docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ntp`
            - here, we got `172.17.0.2` as the IP of the NTP Server container