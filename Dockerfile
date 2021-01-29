FROM python:alpine

RUN pip install requests

WORKDIR /app

ADD app.py .

CMD ./app.py
