#!/bin/bash

# This script deletes all Docker images with the name 'majdabbas99/polybot_build_dev'
image_name=$1

echo "hi $image_name"
prefix="${image_name%%:*}:"

sudo docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" | \
grep "^$prefix" | \
grep -v "$image_name" | \
awk '{print $2}' | xargs -r sudo docker rmi


# sudo docker compose -f docker-compose.polybot.yaml down
# sudo docker compose -f docker-compose.polybot.yaml up -d