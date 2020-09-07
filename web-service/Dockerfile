# How to build: docker build -t 5g-dive/eagleeye/web-service:1.0 .

# Misc:
# Install Docker Nvidia 2.0: https://cnvrg.io/how-to-setup-docker-and-nvidia-docker-2-0-on-ubuntu-18-04/

# TODO: Add latex dependency: docker pull thomasweise/docker-texlive-full
# TODO: Add GPU-Enabled image

FROM nvidia/cuda:10.0-base
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

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
RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y libpython3.7-dev
RUN pip3 install scikit-build
RUN pip3 install opencv-contrib-python-headless

# Get the requirement file
COPY requirements-no-cv.txt /tmp/requirements.txt

# install other requirements
RUN pip3 install Cython

# install req file
RUN pip3 install -r /tmp/requirements.txt

# Folder structure
RUN set -ex \
	&& mkdir /conf \
	&& touch /conf/ews.conf

# Application
COPY ews /app/ews
COPY ext_lib /app/ext_lib
COPY misc /app/misc
COPY outputs /app/outputs
COPY ./ews.py /app

# Expose port
EXPOSE 8080

# Version
ARG VERSION=latest
RUN set -ex \
  && echo "${VERSION}" > /app/VERSION \
  && mkdir log \
  && touch /log/ows.log

WORKDIR /app
CMD ["/usr/bin/python3", "./ews.py", "-c", "/conf/ews.conf"]
