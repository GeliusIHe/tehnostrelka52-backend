import os

import psycopg2
import requests
import telebot
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TG_TOKEN')

DATABASE = {
    'NAME': os.getenv('DB_NAME'),
    'USER': os.getenv('DB_USER'),
    'PASSWORD': os.getenv('DB_PASSWORD'),
    'HOST': os.getenv('DB_HOST'),
    'PORT': os.getenv('DB_PORT')
}

conn = psycopg2.connect(
    dbname=DATABASE['NAME'],
    user=DATABASE['USER'],
    password=DATABASE['PASSWORD'],
    host=DATABASE['HOST'],
    port=DATABASE['PORT']
)
cursor = conn.cursor()

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        code = args[1]
        api_url = 'http://localhost:30183/api/link_telegram/'
        response = requests.post(api_url, json={'code': code, 'chat_id': message.chat.id})
        if response.status_code == 200:
            bot.reply_to(message, "Ваш аккаунт был успешно привязан")
        else:
            bot.reply_to(message, response.json().get('error', 'Произошла ошибка при попытке привязать аккаунт.'))
    else:
        bot.reply_to(message, "Пожалуйста, введите команду в формате /start <Код>")


bot.infinity_polling()
