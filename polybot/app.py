import flask
from flask import request
import os
from polybot.bot import Bot, QuoteBot, ImageProcessingBot
app = flask.Flask(__name__)
from dotenv import load_dotenv
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
Nginx_url = os.getenv('NGINX_URL')
@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_BOT_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'

@app.route(f'/predictions/', methods=['POST'])
def send_detected_objects():
    req = request.get_json()
    print(req)
    uid = req.get('uid')
    chat_id = req.get('chat_id')
    file_path = req.get('file_path')
    image_url = req.get('image_url')
    bot.handle_callback_yolo(uid, chat_id, file_path,image_url)
    return 'Ok'

if __name__ == "__main__":
    bot = ImageProcessingBot(TELEGRAM_BOT_TOKEN, Nginx_url)
    app.run(host='0.0.0.0', port=8443)
