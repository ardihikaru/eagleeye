# How to build: docker build -t 5g-dive/eagleeye/dual-object-detection-service:2.4 .

# Misc:
# Install Docker Nvidia 2.0: https://cnvrg.io/how-to-setup-docker-and-nvidia-docker-2-0-on-ubuntu-18-04/

FROM 5g-dive/eagleeye/dual-object-detection-service-head:2.4
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

ENV ASABFORCECONSOLE 1

# Application
COPY detection /app/detection
#COPY ext_lib /app/ext_lib
#COPY outputs /app/outputs
RUN mkdir -p /app/outputs
COPY ./detection.py /app

# Folder structure
RUN set -ex \
	&& mkdir -p /app/etc \
	&& touch /app/etc/detection.conf \
	&& touch /app/etc/site.conf

# copy default config
COPY etc/detection.conf /app/etc/detection.conf

# Version, log, and config_iles
ARG VERSION=latest
RUN set -ex \
  && echo "${VERSION}" > /app/VERSION \
  && mkdir log \
  && touch /log/ows.log

# copy library from Eagle-data-publisher project
# IMPORTANT: you have to manually copy `eagle_zenoh` folder here first
RUN mkdir -p /opt/eagleeye/eagle_zenoh
COPY eagle_zenoh /opt/eagleeye/eagle_zenoh

WORKDIR /app
CMD ["/usr/bin/python3", "./detection.py", "-c", "/app/etc/detection.conf"]
