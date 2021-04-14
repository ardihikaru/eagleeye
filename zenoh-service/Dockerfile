# How to build: docker build -t 5g-dive/eagleeye/zenoh-service:2.4 .

FROM 5g-dive/eagleeye/core-service:2.4
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

COPY requirements-no-cv.txt /tmp/requirements.txt

# Install rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
RUN rustup toolchain install nightly

# install other requirements
#RUN pip3 install Cython
#
#RUN pip3 install -r /tmp/requirements.txt
#
## Folder structure
#RUN set -ex \
#	&& touch /conf/dual-det/site.conf
#
## Application
##COPY ews /app/ews
##COPY ./ews.py /app
#
## Expose port
##EXPOSE 8080
#
## Version
#ARG VERSION=latest
#RUN set -ex \
#  && echo "${VERSION}" > /app/VERSION

#WORKDIR /app
#CMD ["/usr/bin/python3", "./ews.py", "-c", "/conf/ews/ews.conf"]
