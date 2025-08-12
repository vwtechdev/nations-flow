# pull official base image
FROM python:3.11-slim

# set work directory
WORKDIR /usr/src/nations-flow

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# update system
RUN apt-get update

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .