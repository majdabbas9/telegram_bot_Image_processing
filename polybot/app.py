import flask
from flask import request
import os
from polybot.bot import Bot, QuoteBot, ImageProcessingBot
#from dotenv import load_dotenv

app = flask.Flask(__name__)
#load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_APP_URL = os.getenv('BOT_APP_URL')
Nginx_url = os.getenv('NGINX_URL')

@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_BOT_TOKEN}/', methods=['POST'])
def webhook():
    print("hi")
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    bot = ImageProcessingBot(TELEGRAM_BOT_TOKEN, Nginx_url)
    app.run(host='0.0.0.0', port=8443)
