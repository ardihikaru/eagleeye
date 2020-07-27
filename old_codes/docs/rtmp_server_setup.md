# RTMP Streaming Server Setup

This document is to serve as a guide on setting up a RTMP Server to simulate a drone video stream.

## Requirements

### NGINX 1.14.0
- [DigitalOcean](https://www.digitalocean.com/) published a detailed guide on how you could install NGINX on your Ubuntu 18.04 host machine. You could find the full guide [here](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04).
- Below is the trimmed version of the installation steps for your convenience:
    ```
      $ sudo apt update
      $ sudo apt install nginx 
    ```
 - Note that you should setup your own firewall for NGINX if you plan to use it in a production setting. Again, refer to the guide above by DigitalOcean for more details.
 - You could also find another reference for RTMP Streaming server setup from [here](https://sites.google.com/view/facebook-rtmp-to-rtmps/home).

### RTMP Server
-  [Scaleway Elements](https://www.scaleway.com/en/) published a guide on how you could setup a RTMP Streaming server. You could follow the guide provided by them in this [link](https://www.scaleway.com/en/docs/setup-rtmp-streaming-server/).

### Notes

 - If you are using OBS as your streamer, you could increase the streaming video bitrate to improve stream video quality. In our case, we set it to 10000 kbit/s.

