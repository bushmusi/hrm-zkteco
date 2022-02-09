FROM python:3.9-alpine
LABEL MAINTAINER "Bushra M."

ENV PYTHONUNBUFFERED 1

EXPOSE 4370

# Install dependencies
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Setup directory structure
RUN mkdir /app
WORKDIR /app
COPY ./app/ /app

RUN adduser -D user
USER user