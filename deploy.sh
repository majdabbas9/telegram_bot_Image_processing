#!/bin/bash
path_to_file=$1
telegram_token=$2
s3_bucket_name=$3
app_cert="$APP_CERT"
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
sudo apt update && sudo apt install -y libgl1

# Define version and URLs
VERSION="0.127.0"
DEB_FILE="otelcol_${VERSION}_linux_amd64.deb"
URL="https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v${VERSION}/${DEB_FILE}"
CONFIG_PATH="/etc/otelcol/config.yaml"

# Function to configure otelcol
configure_otelcol() {
    echo "Configuring otelcol to collect host metrics..."

    sudo tee "$CONFIG_PATH" > /dev/null <<EOF
receivers:
  hostmetrics:
    collection_interval: 15s
    scrapers:
      cpu:
      memory:
      disk:
      filesystem:
      load:
      network:
      processes:

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"

service:
  pipelines:
    metrics:
      receivers: [hostmetrics]
      exporters: [prometheus]
EOF

    echo "Restarting otelcol service..."
    sudo systemctl restart otelcol
    sudo systemctl start otelcol

    echo "otelcol configured and restarted."
}

# Main installation logic
if ! command -v otelcol &> /dev/null; then
    echo "otelcol not found. Installing version $VERSION..."

    # Update package list and install wget if needed
    sudo apt-get update
    sudo apt-get -y install wget

    # Download the .deb file
    wget "$URL"

    # Install the package
    sudo dpkg -i "$DEB_FILE"

    # Fix dependencies if needed
    sudo apt-get install -f -y

    # Cleanup
    rm "$DEB_FILE"
fi
sudo cp polybot.service /etc/systemd/system/

# reload daemon and restart the service
sudo systemctl daemon-reload
sudo systemctl restart polybot.service
sudo systemctl enable polybot.service
sudo systemctl start polybot.service
if ! systemctl is-active --quiet polybot.service; then
  echo "❌ polybot.service is not running."
  sudo systemctl status polybot.service --no-pager
  exit 1
fi
printf "%b" "$app_cert" > polybot_cer.crt
env_file="$path_to_file/polybot/.env"
echo "TELEGRAM_BOT_TOKEN=$telegram_token" > "$env_file"
echo "S3_BUCKET_NAME=$s3_bucket_name" >> "$env_file"
echo "NGINX_URL=https://majdprod.fursa.click" >> "$env_file"
# Check if the virtual environment exists
if [ ! -d "$path_to_file/.venv" ]; then  # Check if .venv is a directory
    python3 -m venv "$path_to_file/.venv"
    "$path_to_file/.venv/bin/pip" install -r "$path_to_file/polybot/requirements.txt"
else
    echo "Virtual environment already exists."
fi
