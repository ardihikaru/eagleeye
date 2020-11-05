# How to build: docker build -t 5g-dive/eagleeye/scheduler-service:2.3 .

# Misc:
# Install Docker Nvidia 2.0: https://cnvrg.io/how-to-setup-docker-and-nvidia-docker-2-0-on-ubuntu-18-04/

FROM 5g-dive/eagleeye/nvidia-gpu-opencv:2.3
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

COPY requirements-no-cv.txt /tmp/requirements.txt

# install other requirements
RUN pip3 install Cython

RUN pip3 install -r /tmp/requirements.txt

# Folder structure
RUN set -ex \
	&& mkdir -p /conf/scheduler \
	&& touch /conf/scheduler/scheduler.conf \
	&& touch /conf/scheduler/site.conf

# Application
COPY scheduler /app/scheduler
COPY ext_lib /app/ext_lib
COPY ./scheduler.py /app

# Version
ARG VERSION=latest
RUN set -ex \
  && echo "${VERSION}" > /app/VERSION \
  && mkdir log \
  && touch /log/ows.log

WORKDIR /app
CMD ["/usr/bin/python3", "./scheduler.py", "-c", "/conf/scheduler/scheduler.conf"]
