FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

## Install system dependencies compatible with Alpine
#RUN apk update && apk upgrade && \
#    apk add --no-cache \
#    build-base \
#    libffi-dev \
#    musl-dev \
#    jpeg-dev \
#    zlib-dev \
#    libstdc++ \
#    mesa-gl \
#    libxrender1 \
#    libxext \
#    libsm6
RUN apk update && apk upgrade && \
    apk add --no-cache \
    libxrender1 \
    libsm6
COPY polybot/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . .


# Run the app
CMD ["python3", "-m", "polybot.app"]
