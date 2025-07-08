FROM python:3.10-alpine

WORKDIR /app

# Accept and set secrets via build args
ARG TELEGRAM_BOT_TOKEN
ARG QUEUE_URL
ARG S3_BUCKET_NAME

ENV TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
ENV QUEUE_URL=${QUEUE_URL}
ENV S3_BUCKET_NAME=${S3_BUCKET_NAME}

RUN apk update && apk upgrade && \
    apk add --no-cache \
    build-base \
    libffi-dev \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    libstdc++ \
    mesa-gl \
    libxrender \
    libxext \
    libsm \
    curl

COPY polybot/requirements.txt .

RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt

COPY . .

CMD ["python3", "-m", "polybot.app"]
