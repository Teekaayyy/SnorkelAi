FROM python:3.11-slim

WORKDIR /service

RUN pip install uv --no-cache-dir

COPY app/ ./app/

ENV PYTHONPATH="/service"