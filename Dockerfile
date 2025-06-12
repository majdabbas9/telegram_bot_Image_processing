# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app
# Install only essential system packages (adjust only if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsm6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

Copy polybot/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . .

# Expose port
EXPOSE 8443

# Run the app
CMD ["python3", "-m", "polybot.app"]
