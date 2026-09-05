import os
import threading
from flask import Flask
import telebot
from telebot import types

# 1. Міні-сервер для Render, щоб тримати порт відкритим
app = Flask('')


@app.route('/')
def home():
  return 'Bot is alive!'


def run():
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


def keep_alive():
  t = threading.Thread(target=run)
  t.start()


keep_alive()

# 2. Твій токен бота
TOKEN = '8996181218:AAELaCNDCti2hWlr0sFeSuZbZmLeLHCbfP4'
bot = telebot.TeleBot(TOKEN)


# 3. Головне меню з кнопками
@bot.message_handler(commands=['start'])
def send_welcome(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1 = types.KeyboardButton('🔑 Отримати код авторизації для ПК')
  btn2 = types.KeyboardButton('➕ Додати транзакцію')
  btn3 = types.KeyboardButton('📊 Переглянути прибуток')
  markup.add(btn1, btn2, btn3)

  bot.send_message(
      message.chat.id,
      '🚗 MCARS & FINANCE CONTROL BOT\n\nОберіть дію:',
      reply_markup=markup,
  )


# 4. Обробка натискання на кнопки
@bot.message_handler(func=lambda message: True)
def handle_message(message):
  if message.text == '🔑 Отримати код авторизації для ПК':
    bot.send_message(message.chat.id, 'Тут буде генерація твого ключа для ПК.')
  elif message.text == '➕ Додати транзакцію':
    bot.send_message(message.chat.id, 'Введіть суму та опис через пробіл...')
  elif message.text == '📊 Переглянути прибуток':
    bot.send_message(message.chat.id, 'Ваш поточний прибуток...')
  else:
    bot.send_message(
        message.chat.id, 'Скористайтесь кнопками меню нижче 👇'
    )


if __name__ == '__main__':
  bot.infinity_polling()
