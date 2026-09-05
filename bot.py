import json
import os
import random
import threading
from flask import Flask
import telebot
from telebot import types

# 1. Міні-сервер для Render (щоб тримати порт відкритим)
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

# 2. Токен бота
TOKEN = '8996181218:AAELaCNDCti2hWlr0sFeSuZbZmLeLHCbfP4'
bot = telebot.TeleBot(TOKEN)


# Функції для роботи з файлами JSON
def load_json(filename):
  if os.path.exists(filename):
    with open(filename, 'r', encoding='utf-8') as f:
      try:
        return json.load(f)
      except:
        return {}
  return {}


def save_json(filename, data):
  with open(filename, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# 3. Команда /start з кнопками всередині повідомлення
@bot.message_handler(commands=['start'])
def send_welcome(message):
  markup = types.InlineKeyboardMarkup()
  btn1 = types.InlineKeyboardButton(
      '🔑 Отримати код авторизації для ПК', callback_data='get_key'
  )
  btn2 = types.InlineKeyboardButton(
      '➕ Додати транзакцію', callback_data='add_transaction'
  )
  btn3 = types.InlineKeyboardButton(
      '📊 Переглянути прибуток', callback_data='view_profit'
  )
  markup.add(btn1)
  markup.add(btn2)
  markup.add(btn3)

  bot.send_message(
      message.chat.id,
      '🚗 MCARS & FINANCE CONTROL BOT\n\nОберіть дію:',
      reply_markup=markup,
  )


# 4. Обробка натискань на кнопки всередині повідомлення
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
  user_id = str(call.message.chat.id)

  if call.data == 'get_key':
    code = random.randint(100000, 999999)

    keys_data = load_json('user_keys.json')
    keys_data[user_id] = code
    save_json('user_keys.json', keys_data)

    bot.send_message(
        call.message.chat.id,
        f'🔑 Ваш код для входу в програму на ПК: <code>{code}</code>\n\nВведіть'
        ' цей код у вікні програми при першому запуску.',
        parse_mode='HTML',
    )

  elif call.data == 'add_transaction':
    bot.send_message(
        call.message.chat.id,
        'Введіть суму та опис через пробіл (наприклад: 1500 Купівля деталей)',
    )

  elif call.data == 'view_profit':
    finance_data = load_json('finance_data.json')
    bot.send_message(
        call.message.chat.id,
        f'📊 Ваші збережені дані:\n<code>{finance_data}</code>',
        parse_mode='HTML',
    )


if __name__ == '__main__':
  bot.infinity_polling()
