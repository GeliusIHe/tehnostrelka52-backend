import telebot
import psycopg2
from datetime import datetime, timedelta

TOKEN = '7046099150:AAE39SRoCZ6NzOS0cQs-UbC2S7p2J03J3mA'

DATABASE = {
    'NAME': 'postgres',
    'USER': 'postgres',
    'PASSWORD': 'SD1jkHSKDAD',
    'HOST': '109.107.182.70',
    'PORT': '5432'
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
        try:
            cursor.execute("SELECT * FROM telegram_integration_telegramlink WHERE confirmation_code = %s", (code,))
            data = cursor.fetchone()
            if data:
                if data[4] + timedelta(minutes=10) > datetime.now():
                    cursor.execute(
                        "UPDATE telegram_integration_telegramlink SET telegram_chat_id = %s WHERE confirmation_code = %s",
                        (message.chat.id, code))
                    conn.commit()
                    bot.reply_to(message, "Ваш аккаунт успешно привязан!")
                else:
                    bot.reply_to(message, "Код привязки истек.")
            else:
                bot.reply_to(message, "Неверный код привязки.")
        except Exception as e:
            print(e)
            bot.reply_to(message, "Ошибка при проверке кода.")
    else:
        bot.reply_to(message, "Пожалуйста, отправьте команду в формате: /start ваш_код")


bot.infinity_polling()
