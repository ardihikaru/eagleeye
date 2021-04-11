# How to build: docker build -t 5g-dive/eagleeye/persistance-validation-service:2.4 .

# Misc:
# Install Docker Nvidia 2.0: https://cnvrg.io/how-to-setup-docker-and-nvidia-docker-2-0-on-ubuntu-18-04/

# TODO: Add latex dependency: docker pull thomasweise/docker-texlive-full

FROM 5g-dive/eagleeye/core-service:2.4
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Folder structure
RUN set -ex \
	&& mkdir -p /conf/ \

# Application
COPY pv /app/pv
COPY ./pv.py /app

# Expose port
EXPOSE 8083

# Version
ARG VERSION=latest
RUN set -ex \
  && echo "${VERSION}" > /app/VERSION

WORKDIR /app
CMD ["/usr/bin/python3", "./pv.py", "-c", "/conf/pv.conf"]
