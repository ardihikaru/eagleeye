# How to build: docker build -t 5g-dive/eagleeye/dual-object-detection-service:1.0 .
# How to run: docker run --name dual-det -d --link mongodb:mongo --link redis:redis --link scheduler --link ews -v /home/s010132/devel/eagleeye/object-detection-service/etc/detection.conf:/conf/detection.conf -v /home/s010132/devel/eagleeye/object-detection-service/etc/site.conf:/conf/site.conf -v /home/s010132/devel/eagleeye/object-detection-service/config_files:/app/config_files 5g-dive/eagleeye/dual-object-detection-service:1.0

# Misc:
# Install Docker Nvidia 2.0: https://cnvrg.io/how-to-setup-docker-and-nvidia-docker-2-0-on-ubuntu-18-04/

#FROM 5g-dive/eagleeye/nvidia-gpu-opencv:1.0
FROM 5g-dive/eagleeye/dual-object-detection-service-head:1.0
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Application
COPY detection /app/detection
COPY ext_lib /app/ext_lib
COPY outputs /app/outputs
COPY ./detection.py /app

# Version, log, and config_iles
ARG VERSION=latest
RUN set -ex \
  && echo "${VERSION}" > /app/VERSION \
  && mkdir log \
  && mkdir config_files \
  && touch /log/ows.log

WORKDIR /app
CMD ["/usr/bin/python3", "./detection.py", "-c", "/conf/detection.conf"]
