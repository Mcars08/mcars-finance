import json
import os
import random
import threading
from flask import Flask
import telebot
from telebot import types

# 1. Міні-сервер для Render (щоб тримати порт відкритим безкоштовно)
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


# Функції для роботи з JSON файлами
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


# 3. Головне меню з трьома кнопками знизу
@bot.message_handler(commands=['start'])
def send_welcome(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1 = types.KeyboardButton('🔑 Отримати код авторизації для ПК')
  btn2 = types.KeyboardButton('➕ Додати транзакцію')
  btn3 = types.KeyboardButton('📊 Переглянути прибуток')
  markup.add(btn1)
  markup.add(btn2)
  markup.add(btn3)

  bot.send_message(
      message.chat.id,
      '🚗 MCARS & FINANCE CONTROL BOT\n\nОберіть дію:',
      reply_markup=markup,
  )


# 4. Обробка натискань на кнопки та повідомлень
@bot.message_handler(func=lambda message: True)
def handle_message(message):
  user_id = str(message.chat.id)

  if message.text == '🔑 Отримати код авторизації для ПК':
    code = random.randint(100000, 999999)
    keys_data = load_json('user_keys.json')
    keys_data[user_id] = code
    save_json('user_keys.json', keys_data)

    bot.send_message(
        message.chat.id,
        f'🔑 Ваш код для входу в програму на ПК: <code>{code}</code>\n\nВведіть'
        ' цей код у вікні програми при першому запуску.',
        parse_mode='HTML',
    )

  elif message.text == '➕ Додати транзакцію':
    bot.send_message(
        message.chat.id,
        'Введіть суму та опис через пробіл\nНаприклад: 1500 Купівля деталей',
    )

  elif message.text == '📊 Переглянути прибуток':
    finance_data = load_json('finance_data.json')
    bot.send_message(
        message.chat.id,
        f'📊 Ваші збережені дані:\n<code>{json.dumps(finance_data, ensure_ascii=False, indent=2)}</code>',
        parse_mode='HTML',
    )

  else:
    # Збереження введеної транзакції
    parts = message.text.split(' ', 1)
    try:
      amount = float(parts[0])
      description = parts[1] if len(parts) > 1 else 'Загальне'

      finance_data = load_json('finance_data.json')
      # Додаємо у файл поточні дані
      trans_list = finance_data.get(user_id, [])
      if not isinstance(trans_list, list):
        trans_list = []

      trans_list.append({'amount': amount, 'description': description})
      finance_data[user_id] = trans_list
      save_json('finance_data.json', finance_data)

      sign_str = f'+{amount:.2f}' if amount >= 0 else f'{amount:.2f}'
      bot.send_message(
          message.chat.id,
          '✅ Успішно збережено!\n\n📂 Машина -> Загальне\n📝 Додано з'
          f' Telegram: {sign_str} грн',
      )
    except ValueError:
      bot.send_message(
          message.chat.id,
          '⚠️ Введіть суму та опис через пробіл (наприклад: 1500 Купівля'
          ' деталей)',
      )


if __name__ == '__main__':
  bot.infinity_polling()
