# How to build: docker build -t 5g-dive/eagleeye/nvidia-gpu-opencv:2.3 .

# To install : https://github.com/janza/docker-python3-opencv/blob/master/Dockerfile

FROM nvidia/cuda:10.0-base
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Copy research related work into the container
COPY misc /app/misc

# Install important requirements
RUN apt-get update
RUN apt-get install software-properties-common build-essential apt-utils iputils-ping curl netcat vim -y
RUN apt-get install python3.7 -y

RUN apt-get update \
    && apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        yasm \
        pkg-config \
        libswscale-dev \
        libtbb2 \
        libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libavformat-dev \
        libpq-dev \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y libpython3.7-dev

# Upgrade PIP (important for aioRTC)
RUN pip3 install --upgrade pip
# Required library for RTC (Web-based video streaming)
RUN apt-get install -y libavdevice-dev libavfilter-dev libopus-dev libvpx-dev pkg-config
RUN apt-get install -y libsrtp2-dev
# not listed but needed...
RUN apt install libopencv-dev -y

RUN pip3 install scikit-build
#RUN pip3 install opencv-contrib-python-headless
RUN pip3 install opencv-contrib-python
RUN pip3 install opencv-python

# Copy and Install requirement from web-service
COPY requirements-no-cv.txt /tmp/requirements.txt
RUN pip3 install Cython
RUN pip3 install -r /tmp/requirements.txt

