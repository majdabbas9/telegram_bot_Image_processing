#!/bin/bash
path_to_file=$1
telegram_token=$2
s3_bucket_name_dev=$3
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
sudo apt update && sudo apt install -y libgl1
# Check if ngrok is installed
if command -v ngrok &> /dev/null
then
    echo "✅ ngrok is already installed."
else
    echo "⬇️ ngrok not found. Installing now..."

    # Install ngrok
    curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
    | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
    | sudo tee /etc/apt/sources.list.d/ngrok.list \
    && sudo apt update \
    && sudo apt install -y ngrok
    # Recheck
    if command -v ngrok &> /dev/null
    then
        echo "✅ ngrok installed successfully."
    else
        echo "❌ ngrok installation failed."
        exit 1
    fi
fi

ngrok config add-authtoken 2wKSoZ02WAJ8woqkmFgjtmtqWxH_3h2hacC2fUcvcndDdMBzS
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

env_file="$path_to_file/polybot/.env"
echo "TELEGRAM_BOT_TOKEN=$telegram_token" > "$env_file"
echo "S3_BUCKET_NAME=$s3_bucket_name_dev" >> "$env_file"

# Check if the virtual environment exists
if [ ! -d "$path_to_file/.venv" ]; then  # Check if .venv is a directory
    python3 -m venv "$path_to_file/.venv"
    "$path_to_file/.venv/bin/pip" install -r "$path_to_file/polybot/requirements.txt"
else
    echo "Virtual environment already exists."
fi
