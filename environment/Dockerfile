FROM python:3.11-slim

WORKDIR /service

RUN pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5

COPY app/ ./app/

ENV PYTHONPATH="/service"

CMD ["bash"]