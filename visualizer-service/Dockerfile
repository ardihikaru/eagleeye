# How to build: docker build -t 5g-dive/eagleeye/visualizer-service:2.4 .

# Misc:
# Install Docker Nvidia 2.0: https://cnvrg.io/how-to-setup-docker-and-nvidia-docker-2-0-on-ubuntu-18-04/

# TODO: Add latex dependency: docker pull thomasweise/docker-texlive-full

FROM 5g-dive/eagleeye/dual-object-detection-service-head:2.4
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

COPY requirements-no-cv.txt /tmp/requirements.txt

# install requirements
RUN pip3 install -r /tmp/requirements.txt

# Folder structure
RUN set -ex \
	&& mkdir -p /conf/visualizer/conf \
	&& touch /conf/visualizer/visualizer.conf \
	&& touch /conf/visualizer/site.conf

# Application
COPY visualizer /app/visualizer
#COPY ext_lib /app/ext_lib
COPY ./visualizer.py /app

# Version
ARG VERSION=latest
RUN set -ex \
  && echo "${VERSION}" > /app/VERSION \
  && mkdir log \
  && touch /log/visualizer.log

WORKDIR /app
CMD ["/usr/bin/python3", "./visualizer.py", "-c", "/conf/visualizer/visualizer.conf"]
