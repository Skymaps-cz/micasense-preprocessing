FROM --platform=linux/amd64 ubuntu:latest

ENV LC_ALL=C.UTF-8

RUN apt-get update && \
    apt-get install -y software-properties-common

RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get install -y python3 \
    python3-pip \
    gdal-bin \
    libgdal-dev \
    libgl1-mesa-glx \
    python3-dev \
    zbar-tools \
    exiftool
            
RUN pip install pandas numpy seaborn scipy matplotlib pyNetLogo SALib Cython

ADD . /app
RUN pip install -r /app/requirements.txt

WORKDIR /app