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


# 3. Головне меню
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


# 4. Обробка кнопок та логіка
@bot.message_handler(func=lambda message: True)
def handle_message(message):
  user_id = str(message.chat.id)

  if message.text == '🔑 Отримати код авторизації для ПК':
    code = random.randint(100000, 999999)

    # Зберігаємо ключ у файл user_keys.json
    keys_data = load_json('user_keys.json')
    keys_data[user_id] = code
    save_json('user_keys.json', keys_data)

    bot.send_message(
        message.chat.id,
        f'🔑 Ваш код для входу в програму на ПК: <code>{code} কু</code>\n\nВведіть'
        ' цей код у вікні програми при першому запуску.',
        parse_mode='HTML',
    )

  elif message.text == '➕ Додати транзакцію':
    bot.send_message(
        message.chat.id,
        'Введіть суму та опис через пробіл (наприклад: 1500 Купівля деталей)',
    )

  elif message.text == '📊 Переглянути прибуток':
    finance_data = load_json('finance_data.json')
    bot.send_message(
        message.chat.id, f'📊 Ваші збережені дані: \n<code>{finance_data}</code>',
        parse_mode='HTML',
    )

  else:
    bot.send_message(
        message.chat.id, 'Скористайтесь кнопками меню нижче 👇'
    )


if __name__ == '__main__':
  bot.infinity_polling()
