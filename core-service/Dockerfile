# How to build: docker build -t 5g-dive/eagleeye/core-service:2.4 .

FROM 5g-dive/eagleeye/nvidia-gpu-opencv:2.4
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Install other requirements and Zenoh
RUN pip3 install Cython maturin

# Install Zenoh
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain nightly
ENV PATH="/root/.cargo/bin:${PATH}"
RUN pip3 install eclipse-zenoh==0.5.0b8

# Project Core Codes
COPY ./eagleeye /opt/eagleeye
ENV PYTHONPATH "${PYTHONPATH}:/opt/eagleeye"
