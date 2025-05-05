
path_to_file=$1
source .venv/bin/activate
echo "Path to file: $path_to_file"

ENV_FILE="$path_to_file/polybot/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating .env file..."
    mkdir -p "$(dirname "$ENV_FILE")"
    echo "TELEGRAM_BOT_TOKEN=7628018028:AAGB_oqqKXVykxqCkudMR9zcNEnqeNOqXh4" > "$ENV_FILE"
else
    if ! grep -q "TELEGRAM_BOT_TOKEN=" "$ENV_FILE"; then
        echo "Adding TELEGRAM_BOT_TOKEN to .env file..."
        echo "TELEGRAM_BOT_TOKEN=7628018028:AAGB_oqqKXVykxqCkudMR9zcNEnqeNOqXh4" >> "$ENV_FILE"
    fi
fi

NGROK_PID=$(pgrep -f "ngrok http 8443")
if [ -z "$NGROK_PID" ]; then
    echo "Starting ngrok on port 8443..."
    nohup ngrok http 8443 > /dev/null 2>&1 &
    sed -i '/BOT_APP_URL=/d' $path_to_file/polybot/.env
    sleep 3
else
    echo "ngrok already running (PID $NGROK_PID)"
    exit 0
fi

# Step 2: Get ngrok public URL
NGROK_API_URL="http://127.0.0.1:4040/api/tunnels"
BOT_APP_URL=""
for i in {1..5}; do
    BOT_APP_URL=$(curl -s $NGROK_API_URL | grep -o 'https://[^"]*' | head -n 1)
    if [[ $BOT_APP_URL == https://* ]]; then
        break
    fi
    sleep 2
done

if [ -z "$BOT_APP_URL" ]; then
    echo "Failed to get public URL"
    exit 1
fi

# Step 3: Save the BOT_APP_URL to .env file
export BOT_APP_URL
echo "BOT_APP_URL=$BOT_APP_URL" >> $path_to_file/polybot/.env

ENV_FILE="$path_to_file/polybot/.env"
mkdir -p "$(dirname "$ENV_FILE")"
touch "$ENV_FILE"

.venv/bin/python -m polybot.app


