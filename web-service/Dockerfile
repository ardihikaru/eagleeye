# How to build: docker build -t 5g-dive/eagleeye/web-service:1.0 .

# Misc:
# Install Docker Nvidia 2.0: https://cnvrg.io/how-to-setup-docker-and-nvidia-docker-2-0-on-ubuntu-18-04/

# TODO: Add latex dependency: docker pull thomasweise/docker-texlive-full
# TODO: Add GPU-Enabled image

#FROM python:3.8.5-alpine3.12
#FROM anibali/pytorch:1.5.0-cuda10.2
FROM python:3.7-alpine3.8
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

#SOFTWARE PACKAGES
ENV PACKAGES="\
    dumb-init \
    musl \
    libc6-compat \
    linux-headers \
    build-base \
    bash \
    git \
    ca-certificates \
    freetype \
    libgfortran \
    libgcc \
    libstdc++ \
    openblas \
    tcl \
    tk \
    libssl1.0 \
    "

# PYTHON DATA SCIENCE PACKAGES
ENV PYTHON_PACKAGES="\
    numpy \
    matplotlib \
    scipy \
    scikit-learn \
    pandas \
    nltk \
    "

RUN apk add --no-cache --virtual build-dependencies python3 \
    && apk add --virtual build-runtime \
    build-base python3-dev openblas-dev freetype-dev pkgconfig gfortran \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && ln -sf pip3 /usr/bin/pip \
    && rm -r /root/.cache \
    && pip install --no-cache-dir $PYTHON_PACKAGES \
    && apk del build-runtime \
    && apk add --no-cache --virtual build-dependencies $PACKAGES \
    && rm -rf /var/cache/apk/*

#RUN apk add --no-cache ca-certificates
#RUN set -ex \
#    && apk update \
#    && apk upgrade

# Upgrade pip3
RUN pip3 install --upgrade pip

RUN set -ex \
	&& apk add --virtual .buildenv python3-dev gcc musl-dev git

COPY requirements.txt /tmp/requirements.txt

# install other requirements
RUN pip3 install Cython
RUN pip3 install scikit-build
RUN pip3 install cmake

RUN set -ex \
	&& pip3 install -r /tmp/requirements.txt

# Remove build environment
RUN apk del .buildenv


# Folder structure
RUN set -ex \
	&& mkdir /conf \
	&& touch /conf/ecrapi.conf


# Application
COPY ews /app/ews
COPY ./ews.py /app


# Version
ARG VERSION=latest
RUN set -ex \
  && echo "${VERSION}" > /app/VERSION


WORKDIR /app
CMD ["python3", "ews.py", "-c", "/conf/ews.conf"]
