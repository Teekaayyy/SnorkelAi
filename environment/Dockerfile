FROM python:3.13-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    imagemagick \
    fonts-dejavu-core \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml || true \
    && sed -i 's/<policy domain="resource" name="memory" value="[^"]*"\/>/<policy domain="resource" name="memory" value="512MiB"\/>/' /etc/ImageMagick-6/policy.xml || true

RUN mkdir -p /app/images /app/output/resized /app/output/watermarked

COPY images/ /app/images/
COPY app/ /app/

ENV PYTHONPATH=/app