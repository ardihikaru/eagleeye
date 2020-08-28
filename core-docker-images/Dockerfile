# How to build: docker build -t 5g-dive/eagleeye/web-service:1.0 .

# To install python3-opencv: https://hub.docker.com/r/jjanzic/docker-python3-opencv/dockerfile
# To install : https://github.com/janza/docker-python3-opencv/blob/master/Dockerfile
# Steps:
#### Install Python
## 0. apt-get update
## 1. apt-get install software-properties-common -y
## 2. apt-get install python3.7 -y
## 3. update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
## 4. apt-get install -y python3-pip
## 5. pip3 install scikit-build
## 5. pip3 install numpy  # gak perlu kayaknya
## 6. pip3 install opencv-python

## 2. add-apt-repository ppa:deadsnakes/ppa
## 3. apt-get install python3.7
#### Install opencv
## 1.
#apt-get update \
#    && apt-get install -y \
#        build-essential \
#        cmake \
#        git \
#        wget \
#        unzip \
#        yasm \
#        pkg-config \
#        libswscale-dev \
#        libtbb2 \
#        libtbb-dev \
#        libjpeg-dev \
#        libpng-dev \
#        libtiff-dev \
#        libavformat-dev \
#        libpq-dev \
#    && rm -rf /var/lib/apt/lists/*
## 2. apt-get update
## 3. curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
## 4. python3.7 get-pip.py
## 5. pip3 install numpy
## 6. download and extract opencv
#wget https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip \
#&& unzip ${OPENCV_VERSION}.zip \
#&& mkdir /opencv-${OPENCV_VERSION}/cmake_binary \
#&& cd /opencv-${OPENCV_VERSION}/cmake_binary \
#&& cmake -DBUILD_TIFF=ON \
#  -DBUILD_opencv_java=OFF \
#  -DWITH_CUDA=OFF \
#  -DWITH_OPENGL=ON \
#  -DWITH_OPENCL=ON \
#  -DWITH_IPP=ON \
#  -DWITH_TBB=ON \
#  -DWITH_EIGEN=ON \
#  -DWITH_V4L=ON \
#  -DBUILD_TESTS=OFF \
#  -DBUILD_PERF_TESTS=OFF \
#  -DCMAKE_BUILD_TYPE=RELEASE \
#  -DCMAKE_INSTALL_PREFIX=$(python3.7 -c "import sys; print(sys.prefix)") \
#  -DPYTHON_EXECUTABLE=$(which python3.7) \
#  -DPYTHON_INCLUDE_DIR=$(python3.7 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
#  -DPYTHON_PACKAGES_PATH=$(python3.7 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
#  .. \
#&& make install \
#&& rm /${OPENCV_VERSION}.zip \
#&& rm -r /opencv-${OPENCV_VERSION}

## 2. apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev wget libbz2-dev
## 3. wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz
## 4. tar -xf Python-3.7.4.tgz
## 5. cd Python-3.7.4
## 6. make -j 8

# Misc:
# Install Docker Nvidia 2.0: https://cnvrg.io/how-to-setup-docker-and-nvidia-docker-2-0-on-ubuntu-18-04/

# TODO: Add latex dependency: docker pull thomasweise/docker-texlive-full
# TODO: Add GPU-Enabled image

#FROM python:3.8.5-alpine3.12
#FROM anibali/pytorch:1.5.0-cuda10.2
#FROM python:3.7-alpine3.8
FROM nvidia/cuda:10.0-base
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

#RUN apt add --no-cache ca-certificates
#RUN set -ex \
#    && apt update \
#    && apt upgrade

#RUN sudo apt-get update
#RUN sudo apt install software-properties-common
#RUN sudo apt-get upgrade

# Install important requirements
RUN apt-get update
RUN apt-get install software-properties-common -y
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
    && rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
RUN apt-get install -y python3-pip
RUN pip3 install scikit-build
RUN pip3 install opencv-python

# Upgrade pip3
#RUN pip3 install --upgrade pip

#RUN set -ex \
#	&& apt add --virtual .buildenv python3-dev gcc musl-dev git

#RUN sudo apt-get install -y libprotobuf-dev protobuf-compiler
#RUN sudo apt-get install gcc musl-dev git -y
#RUN sudo apt-get install -y libgl1-mesa-dev
#RUN sudo apt-get install python3.8-dev gcc musl-dev git python3-pip -y

#RUN pip3 install --upgrade pip

COPY requirements.txt /tmp/requirements.txt

# install other requirements
#RUN pip install Cython
#RUN pip install scikit-build
#RUN pip install cmake

#RUN set -ex \
#	&& pip3 install -r /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt

# Remove build environment
#RUN apt del .buildenv


# Folder structure
RUN set -ex \
	&& sudo mkdir /conf \
	&& sudo touch /conf/ews.conf


# Application
COPY ews /app/ews
COPY ext_lib /app/ext_lib
COPY misc /app/misc
COPY ./ews.py /app


# Version
ARG VERSION=latest
RUN set -ex \
  && echo "${VERSION}" > /app/VERSION


WORKDIR /app
CMD ["python3", "ews.py", "-c", "/conf/ews.conf"]
