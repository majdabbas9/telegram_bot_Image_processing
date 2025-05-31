#!/bin/bash
path_to_file=$1
ipYolo=$2
if [ -z "$path_to_file" ] || [ -z "$ipYolo" ]; then
    echo "You didn't give all the arguments"
    exit 1
fi

echo "Path to file: $path_to_file"

NGROK_PID=$(pgrep -f "ngrok http 8443")
if [ -z "$NGROK_PID" ]; then
    echo "Starting ngrok on port 8443..."
    nohup ngrok http 8443 > /dev/null 2>&1 &
    sed -i '/BOT_APP_URL=/d' $path_to_file/polybot/.env
    sleep 3
else
    echo "ngrok already running (PID $NGROK_PID)"
    echo "running"
    cd $path_to_file
    .venv/bin/python -m polybot.app
fi

# Step 2: Get ngrok public URL
BOT_APP_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
sed -i '/^ipYolo=/d' "$path_to_file/polybot/.env"

echo >> "$path_to_file/polybot/.env"
echo "ipYolo=$ipYolo" >> "$path_to_file/polybot/.env"
echo "BOT_APP_URL=$BOT_APP_URL" >> "$path_to_file/polybot/.env"
echo "running.."
sleep 2
cd $path_to_file
.venv/bin/python -m polybot.app
