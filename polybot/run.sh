path_to_file=$1
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
    sleep 2
    .venv/bin/python -m polybot.app
    exit 0
fi

# Step 2: Get ngrok public URL
BOT_APP_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o '"public_url":"[^"]*' | grep -o '[^"]*$')
sudo echo "BOT_APP_URL=$BOT_APP_URL" >> $path_to_file/polybot/.env
echo "running.."
sleep 2
.venv/bin/python -m polybot.app
