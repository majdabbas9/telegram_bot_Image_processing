FROM python:3.10-alpine

WORKDIR /app

# Accept build argument
ARG SECRETS

# Optional: use env arg inside image (for debugging or ENV config)
ENV ENV=$SECRETS

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
