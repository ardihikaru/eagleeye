# How to build: docker build -t 5g-dive/eagleeye/web-service:1.0 .

# Misc:
# Install Docker Nvidia 2.0: https://cnvrg.io/how-to-setup-docker-and-nvidia-docker-2-0-on-ubuntu-18-04/

# TODO: Add latex dependency: docker pull thomasweise/docker-texlive-full
# TODO: Add GPU-Enabled image

#FROM python:3.8.5-alpine3.12
FROM anibali/pytorch:1.5.0-cuda10.2
#FROM python:3.7-alpine3.8
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

#RUN apt add --no-cache ca-certificates
#RUN set -ex \
#    && apt update \
#    && apt upgrade

RUN sudo apt-get update
RUN sudo apt install software-properties-common
#RUN sudo apt-get upgrade

# Upgrade pip3
#RUN pip3 install --upgrade pip

#RUN set -ex \
#	&& apt add --virtual .buildenv python3-dev gcc musl-dev git

RUN sudo apt-get install -y libprotobuf-dev protobuf-compiler
RUN sudo apt-get install gcc musl-dev git -y
RUN sudo apt-get install -y libgl1-mesa-dev
#RUN sudo apt-get install python3.8-dev gcc musl-dev git python3-pip -y

#RUN pip3 install --upgrade pip

COPY requirements.txt /tmp/requirements.txt

# install other requirements
RUN pip install Cython
RUN pip install scikit-build
RUN pip install cmake

#RUN set -ex \
#	&& pip3 install -r /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

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
