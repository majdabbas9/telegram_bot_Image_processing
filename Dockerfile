FROM python:3.10-alpine

WORKDIR /app

# Install system dependencies compatible with Alpine
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
# Copy only requirements file for layer caching
COPY polybot/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt



# Copy the app
COPY . .


# Run the app
CMD ["python3", "-m", "polybot.app"]
