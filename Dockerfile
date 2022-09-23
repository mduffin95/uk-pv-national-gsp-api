FROM python:3.10-slim-bullseye

# copy files over
COPY ./src /app/src
COPY ./requirements.txt /app/requirements.txt

# set working directory
WORKDIR /app

# install requirements
RUN apt-get update -y
RUN apt-get install -y gdal-bin libgdal-dev g++
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y git
RUN pip install git+https://github.com/SheffieldSolar/PV_Live-API#pvlive_api

# make sure 'src' is in python path - this is so imports work
ENV PYTHONPATH=${PYTHONPATH}:/app/src
