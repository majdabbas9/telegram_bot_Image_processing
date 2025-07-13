import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
from polybot.img_proc import Img
import threading
from collections import defaultdict
import re
import requests
class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(1.5)  # wait for webhook removal
        logger.info(f"Setting webhook to URL: {telegram_chat_url}/{token}/")
        # set the webhook URL without providing a certificate (handled by LB)
        self.telegram_bot_client.set_webhook(
            url=f'{telegram_chat_url}/{token}/',
            timeout=60
        )

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_help(self, chat_id, help_text):
        self.telegram_bot_client.send_message(chat_id, help_text, parse_mode="HTML")

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        user_id = msg['from']['id']
        new_file_path = os.path.join('last_image_inserted_by_clients', f"{user_id}.jpg")

        # Create the directory if it doesn't exist
        os.makedirs('last_image_inserted_by_clients', exist_ok=True)

        # Write the file only if it doesn't already exist
        with open(new_file_path, 'wb') as user_photo:
            user_photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])


class ImageProcessingBot(Bot):
    media_groups = defaultdict(list)
    timers = {}
    def handle_image_processing(self, msg, the_img, caption,chat_id):
        if (value := the_img.check_rotate_in_filtername(caption)) is not None:
            the_img.rotate_in_steps(value)
            new_path = the_img.save_img()
            self.send_photo(msg['chat']['id'], new_path)

        elif caption in ['segment', 's']:
            the_img.segment()
            new_path = the_img.save_img()
            self.send_photo(msg['chat']['id'], new_path)

        elif caption.replace(" ", "") in ['saltandpepper', "s&p"]:
            the_img.salt_n_pepper()
            new_path = the_img.save_img()
            self.send_photo(msg['chat']['id'], new_path)

        elif caption in ['contour', 'c']:
            the_img.contour()
            new_path = the_img.save_img()
            self.send_photo(msg['chat']['id'], new_path)

        elif caption in ['blur', 'b']:
            the_img.blur()
            new_path = the_img.save_img()
            self.send_photo(msg['chat']['id'], new_path)

        elif caption in ['detect', 'd']:
            the_img.detect_objects(chat_id)
        else :
            self.send_photo(msg['chat']['id'], 'no such command')

    def process_media_group(self, group_id, chat_id):
        try:
            messages = self.media_groups.pop(group_id, [])
            self.timers.pop(group_id, None)

            if len(messages) < 2:
                self.send_text(chat_id, "Need at least 2 images in the album to perform concat.")
                return

            img_base = Img(self.download_user_photo(messages[0]))
            img2 = Img(self.download_user_photo(messages[1]))
            caption = messages[0]['caption'].replace(" ", "")
            if (match := re.match(r'^(cc|concat)(h|v|horizontal|vertical|)$', caption)) is not None:
                concat_type = match.groups()[1]
                if concat_type in ['h', 'horizontal', '']:
                    concat_type = 'horizontal'
                elif concat_type in ['v', 'vertical']:
                    concat_type = 'vertical'
                img_base.concat(img2,direction=concat_type)
                new_path = img_base.save_img()
                self.send_photo(chat_id, new_path)

        except Exception as e:
            logger.error(f"Error in process_media_group: {e}")
            self.send_text(chat_id, e)

    def handle_message(self, msg):
        try :
            logger.info(f'Incoming message: {msg}')
            user_id = msg['from']['id']
            chat_id = msg['chat']['id']
            msg_without_numbers = ''.join(c for c in msg['text'].replace(" ","").lower() if not c.isdigit() and c != '-') if not self.is_current_msg_photo(msg) else ""
            commands = ['rotate', 'r', 'saltandpepper', 's&p', 'segment', 's', 'contour', 'c','blur','b','d','detect']
            if self.is_current_msg_photo(msg):
                file_path = self.download_user_photo(msg)
                #################################################################
                if 'media_group_id' in msg:
                    group_id = msg['media_group_id']
                    self.media_groups[group_id].append(msg)
                    if group_id not in self.timers:
                        timer = threading.Timer(1.5, self.process_media_group, args=(group_id, chat_id))
                        self.timers[group_id] = timer
                        timer.start()
                else :
                    if 'caption' not in msg:
                        self.send_photo(msg['chat']['id'], 'no such command')
                        return
                    caption = msg['caption'].lower() if 'caption' in msg else ''
                    the_img = Img(file_path)
                    self.handle_image_processing(msg, the_img, caption,chat_id)

            elif msg_without_numbers in commands:
                filename = f"{user_id}.jpg"
                filepath = os.path.join('last_image_inserted_by_clients', filename)
                if filepath and os.path.exists(filepath):
                    the_img = Img(filepath)
                    self.handle_image_processing(msg, the_img, msg["text"],chat_id  )
                else:
                    self.send_text(chat_id, "No previous image found.")

            elif msg['text'].lower() in ["help", "commands", "help!"]:
                help_message = (
                    "<b>🛠 PolyBot Help Menu</b>\n\n"
                    "<b>🖼 Basic Commands:</b>\n"
                    "• <code>rotate</code> or <code>r</code> — Rotates the image by 90° by default \n"
                    "• <code>rotate 2</code> or <code>r 2</code> to rotate in 180 degree\n"
                    "• you can do a -180 degree rotation by using <code>rotate -2</code> or <code>r -2</code>\n\n"
                    "• <code>salt and pepper</code> or <code>s&p</code> — Apply salt and pepper noise\n"
                    "• <code>segment</code> or <code>s</code> — Segment the image\n"
                    "• <code>contour</code> or <code>c</code> — Apply contour detection\n\n"
                    "<b>🧩 Concat Images:</b>\n"
                    "Send 2 photos as an album with one of these captions:\n"
                    "• <code>concat</code> — Horizontal by default\n"
                    "• <code>concat h</code> or <code>concat horizontal</code> — Horizontal concat\n"
                    "• <code>concat v</code> or <code>concat vertical</code> — Vertical concat\n\n"
                    "<b>ℹ️ Tips:</b>\n"
                    "• Send a photo, then type a command to apply filters.\n"
                    "• Say <code>hello</code> or <code>start</code> to begin.\n"
                    "• a command with paramters will work without adding any spaces.\n"
                )
                self.send_help(chat_id, help_message)
            elif msg["text"].lower() in ["hi","hello","hi!","hello!","start","start!"]:
                self.send_text(msg['chat']['id'], "Hello! I'm PolyBot, your image processing assistant. Type 'help' to see what I can do!")
            elif msg["text"].lower() in ["majd"]:
                self.send_text(msg['chat']['id'], "majd abbas")
            elif msg["text"].lower() in ["how are you","how are you!"]:
                self.send_text(msg['chat']['id'], "I am good , How are you?!")
            elif msg["text"].lower() in ["hi how are you ?"]:
                self.send_text(msg['chat']['id'], "I am good , How are you?!")
            elif msg["text"].lower() in ["what are you doing today ?"]:
                self.send_text(msg['chat']['id'], "I am here to help you with image processing tasks! Just send me a photo and a command.")
            elif msg["text"].lower() in ["my name is majd"]:
                self.send_text(msg['chat']['id'], "Nice to meet you, Majd! How can I assist you today?")
            else:
                self.send_text(msg['chat']['id'], f'No commands like that!')
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.send_text(msg['chat']['id'], f"An error occurred: {e}")
    def handle_callback_yolo(self,uid,chat_id,file_path,image_url):
        the_img = Img(file_path)
        the_img.get_detected_objects(uid,image_url)
        new_path = the_img.save_img()
        self.send_photo(chat_id, new_path)

