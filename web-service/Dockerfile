# How to build: docker build -t 5g-dive/eagleeye/web-service:2.2 .

# Misc:
# Install Docker Nvidia 2.0: https://cnvrg.io/how-to-setup-docker-and-nvidia-docker-2-0-on-ubuntu-18-04/

# TODO: Add latex dependency: docker pull thomasweise/docker-texlive-full

FROM 5g-dive/eagleeye/nvidia-gpu-opencv:2.2
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
	&& mkdir -p /conf/ews/conf \
	&& mkdir -p /conf/dual-det/conf \
	&& touch /conf/ews/ews.conf \
	&& touch /conf/ews/site.conf \
	&& touch /conf/dual-det/site.conf

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
CMD ["/usr/bin/python3", "./ews.py", "-c", "/conf/ews/ews.conf"]
