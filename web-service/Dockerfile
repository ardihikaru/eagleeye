# How to build: docker build -t 5g-dive/eagleeye/web-service:1.0 .

# Misc:
# Install Docker Nvidia 2.0: https://cnvrg.io/how-to-setup-docker-and-nvidia-docker-2-0-on-ubuntu-18-04/

# TODO: Add latex dependency: docker pull thomasweise/docker-texlive-full
# TODO: Add GPU-Enabled image

FROM 5g-dive/eagleeye/nvidia-gpu-opencv:1.1
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

#RUN pip3 install --upgrade pip

COPY requirements.txt /tmp/requirements.txt

# install other requirements
RUN pip3 install Cython
#RUN pip install scikit-build
#RUN pip install cmake

RUN pip3 install -r /tmp/requirements.txt

# Folder structure
RUN set -ex \
	&& mkdir /conf \
	&& touch /conf/ews.conf

# Application
COPY ews /app/ews
COPY ext_lib /app/ext_lib
COPY misc /app/misc
COPY ./ews.py /app

# Version
#ARG VERSION=latest
#RUN set -ex \
#  && echo "${VERSION}" > /app/VERSION

WORKDIR /app
CMD ["python3", "ews.py", "-c", "/conf/ews.conf"]
