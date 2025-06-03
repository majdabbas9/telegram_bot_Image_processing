#!/bin/bash
path_to_file=$1
ipYolo=$2
if [ -z "$path_to_file" ] || [ -z "$ipYolo" ]; then
    echo "You didn't give all the arguments"
    exit 1
fi
echo "Path to file: $path_to_file"
sed -i '/^ipYolo=/d' "$path_to_file/polybot/.env"
echo "ipYolo=$ipYolo" >> "$path_to_file/polybot/.env"
sleep 2
cd $path_to_file
.venv/bin/python -m polybot.app
