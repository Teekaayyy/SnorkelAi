FROM python:3.13-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    imagemagick \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/images /app/output/resized /app/output/watermarked

COPY images/ /app/images/