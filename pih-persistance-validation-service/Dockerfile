# How to build: `$ docker build -f Dockerfile -t 5g-dive/eagleeye/pv:1.0 .`
# Run daemon: `$ docker run -d --name pv-svc --network host 5g-dive/eagleeye/pv:1.0`
# Run: `$ docker run --name pv-svc --network host 5g-dive/eagleeye/pv:1.0`
# Run: `$ docker run --name pv-1-svc --network host --rm -it -v /home/s010132/devel/eagleeye/pih-persistance-validation-service/etc/site-1.conf:/app/etc/site.conf 5g-dive/eagleeye/pv:1.0`
# Test container: `$ docker run -it --rm 5g-dive/eagleeye/pv:1.0 bash`
# remove container: `$ docker container rm -f pv-svc`

# why not using alphine: https://pythonspeed.com/articles/alpine-docker-python/
FROM 5g-dive/eagleeye/pycore-compact:1.0 as base
MAINTAINER Muhammad Febrian Ardiansyah (mfardiansyah.ee08@nycu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

ENV ASABFORCECONSOLE 1

# We copy just the requirements.txt first to leverage Docker cache
WORKDIR /usr/local
COPY ./requirements.txt /usr/local/requirements.txt
# and install it
RUN apt-get update
RUN pip install --upgrade pip
RUN apt-get update \
	&& pip install -r requirements.txt

WORKDIR /app
ARG VERSION=latest
RUN echo "${VERSION}" > /app/VERSION
RUN mkdir -p /app/etc
COPY etc/pv.conf /app/etc/
RUN touch /app/etc/site.conf
COPY pv /app/pv
COPY ./pv.py /app

CMD ["/usr/local/bin/python", "./pv.py", "-c", "etc/pv.conf"]
