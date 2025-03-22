FROM python:3.9-slim-buster

WORKDIR /api

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /api

CMD python api.py
