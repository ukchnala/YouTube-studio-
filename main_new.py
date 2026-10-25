import os
import threading
from flask import Flask
import telebot

# Render ke environment variable se token uthayega
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


@app.route('/')
def home():
  return 'YouTube Automation Bot is active and running!'


@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(
      message,
      'Namaste! Aapka YouTube automation bot Render par successfully live ho'
      ' chuka hai!',
  )


@bot.message_handler(func=lambda message: True)
def echo_all(message):
  bot.reply_to(message, 'Aapka message mil gaya hai: ' + message.text)


def run_bot():
  bot.infinity_polling()


if __name__ == '__main__':
  # Bot ko background thread mein chalayenge taki Flask server port bind kar sake
  t = threading.Thread(target=run_bot)
  t.daemon = True
  t.start()

  # Render ke diye gaye PORT par Flask app start hoga
  port = int(os.environ.get('PORT', 10000))
  app.run(host='0.0.0.0', port=port)
  
