FROM python:3.8-slim

ENV TZ="Europe/Moscow"
ARG VK_TOKEN

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD python run.py $VK_TOKEN