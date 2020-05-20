# Simple HTTP Streaming with FFmpeg

This document is to serve as a guide on performing a single video file streaming via HTTP. The video source file will be an offline file on host local storage. The video then will be streamed using the [FFmpeg](https://www.ffmpeg.org/) project.

## Installation

 - Install x264 library
```
sudo apt-get install -y libx264-dev
``` 
- Download & Install FFmpeg 3.4.7 tarball
```
sudo apt-get install -y nasm
wget https://www.ffmpeg.org/releases/ffmpeg-3.4.7.tar.xz
tar -xf ffmpeg-3.4.7.tar.xz
cd ffmpeg-3.4.7/
./configure --enable-gpl --enable-libx264
make -j4
```

## Setup
Note that all of the command below needs to be run inside your ffmpeg folder!

### Single Stream Setup for Destination Server
 - On the destination server, start ffserver by running the command below:
```
./ffserver -f single_stream.conf
```
 - The `single_stream.conf` file can be found below:
```
HTTPPort 10000 # Update as necessary
HTTPBindAddress 0.0.0.0
MaxHTTPConnections 1000
MaxClients 1000
MaxBandwidth 100000
CustomLog - 

<Feed stream-1.ffm>
  File /tmp/stream-1.ffm
  FileMaxSize 1G
</Feed>

<Stream stream-1.flv>
    Feed stream-1.ffm
    Format flv # Update as necessary
    NoAudio
    VideoCodec libx264
    VideoFrameRate 30 # Update as necessary
    VideoSize 1920x1080 # Update as necessary
    VideoBitRate 10000
    AVOptionVideo flags +global_header
</Stream>
```
 - For more reference on ffserver, you can visit [this link](https://trac.ffmpeg.org/wiki/ffserver) 

### Single Stream Setup for Source Server
 - Make sure that FFmpeg is also installed in your source server
 - If yes, then you can stream a video file to the destination server with:
```
./ffmpeg -re -i ./video_file.mp4 http://192.168.1.100:10000/stream-1.ffm
```
- Remember to update the above IP address, port number and stream name 
(e.g.: `stream-1.ffm`) as necessary
