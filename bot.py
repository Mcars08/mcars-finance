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


# 3. Команда /start з інлайн-кнопками всередині повідомлення
@bot.message_handler(commands=['start'])
def send_welcome(message):
  markup = types.InlineKeyboardMarkup(row_width=1)
  btn1 = types.InlineKeyboardButton(
      '🔑 Отримати код авторизації для ПК', callback_data='btn_key'
  )
  btn2 = types.InlineKeyboardButton(
      '➕ Додати транзакцію', callback_data='btn_add'
  )
  btn3 = types.InlineKeyboardButton(
      '📊 Переглянути прибуток', callback_data='btn_profit'
  )
  markup.add(btn1, btn2, btn3)

  bot.send_message(
      message.chat.id,
      '🚗 MCARS & FINANCE CONTROL BOT\n\nОберіть дію:',
      reply_markup=markup,
  )


# 4. Обробка натискань на інлайн-кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
  user_id = str(call.message.chat.id)

  if call.data == 'btn_key':
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

  elif call.data == 'btn_add':
    bot.send_message(
        call.message.chat.id,
        'Введіть суму та опис через пробіл\nНаприклад: 1500 Купівля деталей',
    )

  elif call.data == 'btn_profit':
    finance_data = load_json('finance_data.json')
    bot.send_message(
        call.message.chat.id,
        f'📊 Ваші збережені дані:\n<code>{json.dumps(finance_data, ensure_ascii=False, indent=2)}</code>',
        parse_mode='HTML',
    )


# 5. Обробка введення суми для транзакцій (якщо користувач просто пише текст)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
  user_id = str(message.chat.id)
  parts = message.text.split(' ', 1)
  try:
    amount = float(parts[0])
    description = parts[1] if len(parts) > 1 else 'Загальне'

    finance_data = load_json('finance_data.json')
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
        '⚠️ Скористайтесь кнопками меню вище або введіть суму та опис через'
        ' пробіл (наприклад: 1500 Купівля деталей)',
    )


if __name__ == '__main__':
  bot.infinity_polling()
