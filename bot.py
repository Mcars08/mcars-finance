import os
import threading
from flask import Flask
import telebot

# Налаштування міні-сервера для Render, щоб порт завжди був відкритим
app = Flask('')


@app.route('/')
def home():
  return 'Bot is alive!'


def run():
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


def keep_alive():
  t = threading.Thread(target=run)
  t.start()


# Запускаємо веб-сервер у фоні
keep_alive()

# === СЮДИ ВСТАВ СВІЙ ТОКЕН БОТА ===
TOKEN = '8996181218:AAELaCNDCti2hWlr0sFeSuZbZmLeLHCbfP4'
bot = telebot.TeleBot(TOKEN)


# Обробка команди /start
@bot.message_handler(commands=['start'])
def send_welcome(bot_message):
  bot.reply_to(
      bot_message,
      'Привіт! Бот успішно працює в хмарі на Render і готовий до роботи!',
  )


# Обробка звичайних текстових повідомлень
@bot.message_handler(func=lambda message: True)
def echo_all(message):
  bot.reply_to(message, f'Отримав твоє повідомлення: {message.text}')


# Нескінченний цикл опитування Telegram
if __name__ == '__main__':
  bot.infinity_polling()