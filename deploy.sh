#!/bin/bash
path_to_file=$1
telegram_token=$2
# copy the .servcie file
#sudo cp polybot.service /etc/systemd/system/
#
## reload daemon and restart the service
#sudo systemctl daemon-reload
#sudo systemctl restart polybot.service
#sudo systemctl enable polybot.service
#sudo systemctl start polybot.service
# Check if the service is active
#if ! systemctl is-active --quiet polybot.service; then
#  echo "❌ polybot.service is not running."
#  sudo systemctl status polybot.service --no-pager
#  exit 1
#fi
env_file="$path_to_file/polybot/.env"
if [ ! -f "$env_file" ]; then
    echo ".env file does NOT exist — creating it now."
    echo "TELEGRAM_BOT_TOKEN=$telegram_token" > "$env_file"

    echo ".env file created and token added."
else
    echo ".env file already exists."
fi

# Check if the virtual environment exists
if [ ! -d "$path_to_file/.venv" ]; then  # Check if .venv is a directory
    python3 -m venv "$path_to_file/.venv"
    "$path_to_file/.venv/bin/pip" install -r "$path_to_file/polybot/requirements.txt"
else
    echo "Virtual environment already exists."
fi
