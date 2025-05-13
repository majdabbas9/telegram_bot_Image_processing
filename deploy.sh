#!/bin/bash

# copy the .servcie file
sudo cp polybot.service /etc/systemd/system/

# reload daemon and restart the service
sudo systemctl daemon-reload
sudo systemctl restart polybot.service
sudo systemctl enable polybot.service
sudo systemctl start polybot.service
# Check if the service is active
if ! systemctl is-active --quiet polybot.service; then
  echo "❌ polybot.service is not running."
  sudo systemctl status polybot.service --no-pager
  exit 1
fi