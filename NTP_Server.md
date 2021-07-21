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
         - Result will be like this:
           ``` 
           server 172.17.0.2, stratum 3, offset -0.001869, delay 0.02571
           17 Jun 08:56:48 ntpdate[5444]: adjust time server 172.17.0.2 offset -0.001869 sec 
           ```
    - Turn off system's NTP sync: `$ timedatectl set-ntp off`
    - Then, set this Host Machine to sync with its container-based NTP Server
        `$ sudo ntpdate -u 172.17.0.2`
    - How to check NTP's Docker container IP: 
        `$ docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container_name_or_id`
        - In this case, we use name `ntp`, so we can run:
        `$ docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ntp`
            - here, we got `172.17.0.2` as the IP of the NTP Server container
    - How to Drone connects to the Server's NTP Server
        1. Check current time status: `$ timedatectl status`
           ```
           Local time: 三 2021-06-23 12:14:48 CST
           Universal time: 三 2021-06-23 04:14:48 UTC
           RTC time: 三 2021-06-23 04:14:48
           Time zone: Asia/Taipei (CST, +0800)
           System clock synchronized: yes
           systemd-timesyncd.service active: yes   ---------------> We plan to turn off this one!
           RTC in local TZ: no
           ```
        2. Turn off system's NTP sync: `$ timedatectl set-ntp off`
           ``` 
           $ timedatectl set-ntp off
           ==== AUTHENTICATING FOR org.freedesktop.timedate1.set-ntp ===
                           network time synchronization shall be enabled.
           Authenticating as: popeye,,, (popeye)
           Password: 
           ==== AUTHENTICATION COMPLETE ===  
           ```
        3. Once turned off, check again: `$ timedatectl status`
           ```
           Local time: 三 2021-06-23 12:18:41 CST
           Universal time: 三 2021-06-23 04:18:41 UTC
           RTC time: 三 2021-06-23 04:18:41
           Time zone: Asia/Taipei (CST, +0800)
           System clock synchronized: yes  --------------------> we need this to be turned off as well!
           systemd-timesyncd.service active: no   ---------------> It is turned off now!
           RTC in local TZ: no
           ```
        4. Install ntp client: `$ sudo apt install ntpdate`
        5. Update the NTP to the target NTP Server: `$ sudo ntpdate -u 192.168.1.10`
           ```
           Local time: 三 2021-06-23 12:18:41 CST
           Universal time: 三 2021-06-23 04:18:41 UTC
           RTC time: 三 2021-06-23 04:18:41
           Time zone: Asia/Taipei (CST, +0800)
           System clock synchronized: no  --------------------> we need this to be turned off as well!
           systemd-timesyncd.service active: no   ---------------> It is turned off now!
           RTC in local TZ: no
           ```
           - If you also have `NTP service: active`, this should be `NTP service: inactive`.
        6. If the offset time still vary, try to restart the dockerized NTP Server, and perform **step-5** again.
        7. Do not forget to run the bash script: `$ . sync_time.sh`
            - IP `192.168.1.10` is the Server IP of the NTP Server. Please change it accordingly. :)