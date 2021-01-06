# How to build: docker build -t 5g-dive/eagleeye/core-service:2.4 .

FROM 5g-dive/eagleeye/nvidia-gpu-opencv:2.4
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Project Core Codes
COPY ./eagleeye /opt/eagleeye
ENV PYTHONPATH "${PYTHONPATH}:/opt/eagleeye"
