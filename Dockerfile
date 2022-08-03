FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive
ENV LANGUAGE ru_RU.UTF-8
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8
ENV running_docker=TRUE

RUN mkdir -p /usr/local/workdir

RUN apt-get -y update
RUN apt-get install -y wget gnupg2 unzip python3-pip locales iputils-ping curl tzdata
RUN locale-gen ru_RU.UTF-8 && dpkg-reconfigure locales

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN dpkg-reconfigure --frontend noninteractive tzdata

COPY ./requirements.txt /usr/local/workdir
RUN pip3 install -r /usr/local/workdir/requirements.txt

COPY ./ /usr/local/workdir
RUN rm -rf /usr/local/workdir/storage/*

WORKDIR /usr/local/workdir
ENTRYPOINT python3 main.py