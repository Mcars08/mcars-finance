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

# Словник для збереження поточного кроку користувача
user_state = {}


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


# 3. Головне меню (кнопки знизу)
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


# 4. Обробка текстових повідомлень та кнопок знизу
@bot.message_handler(func=lambda message: True)
def handle_message(message):
  user_id = str(message.chat.id)

  if message.text == '🔑 Отримати код авторизації для ПК':
    code = random.randint(100000, 999999)
    keys_data = load_json('user_keys.json')
    keys_data[user_id] = code
    save_json('user_keys.json', keys_data)

    # Бот надсилає згенерований код у чат повідомленням
    bot.send_message(
        message.chat.id,
        f'🔑 Ваш код для входу в програму на ПК: <code>{code}</code>\n\nВведіть'
        ' цей код у вікні програми при першому запуску.',
        parse_mode='HTML',
    )

  elif message.text == '➕ Додати транзакцію':
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('Машина', callback_data='cat_Машина'),
        types.InlineKeyboardButton('Бізнес', callback_data='cat_Бізнес'),
        types.InlineKeyboardButton('Крипта', callback_data='cat_Крипта'),
        types.InlineKeyboardButton('Покупки', callback_data='cat_Покупки'),
    )
    markup.add(types.InlineKeyboardButton('Подорожі', callback_data='cat_Подорожі'))

    bot.send_message(
        message.chat.id, 'Оберіть категорію:', reply_markup=markup
    )

  elif message.text == '📊 Переглянути прибуток':
    finance_data = load_json('finance_data.json')
    user_fin = finance_data.get(user_id, {'income': 0.0, 'expense': 0.0})
    income = user_fin.get('income', 0.00)
    expense = user_fin.get('expense', 0.00)
    profit = income - expense

    text = (
        '📊 ВАШ ОСОБИСТИЙ БАЛАНС:\n\n'
        f'🟢 Доходи: {income:.2f} грн\n'
        f'🔴 Витрати: {expense:.2f} грн\n'
        f'💰 Чистий прибуток: {profit:.2f} грн'
    )
    bot.send_message(message.chat.id, text)

  else:
    if user_id in user_state and user_state[user_id].get('step') == 'waiting_amount':
      data = user_state[user_id]
      category = data['category']
      op_type = data['type']

      parts = message.text.split(' ', 1)
      try:
        amount = float(parts[0])
        description = parts[1] if len(parts) > 1 else 'Загальне'

        finance_data = load_json('finance_data.json')
        if user_id not in finance_data:
          finance_data[user_id] = {'income': 0.0, 'expense': 0.0}

        if op_type == '+':
          finance_data[user_id]['income'] += amount
          sign_str = f'+{amount:.2f}'
        else:
          finance_data[user_id]['expense'] += amount
          sign_str = f'-{amount:.2f}'

        save_json('finance_data.json', finance_data)

        bot.send_message(
            message.chat.id,
            '✅ Успішно збережено!\n\n📂 '
            f'{category} -> {description}\n📝 Додано з Telegram: {sign_str} грн',
        )
        del user_state[user_id]
      except ValueError:
        bot.send_message(
            message.chat.id,
            '⚠️ Будь ласка, введіть суму та опис коректно (наприклад: 1500 Купівля'
            ' деталей або просто 500)',
        )
    else:
      bot.send_message(
          message.chat.id, 'Скористайтесь кнопками меню нижче 👇'
      )


# 5. Обробка натискань на інлайн-кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
  user_id = str(call.message.chat.id)

  if call.data.startswith('cat_'):
    category = call.data.split('_')[1]
    user_state[user_id] = {'category': category}

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('➕ Дохід (+)', callback_data='op_plus'),
        types.InlineKeyboardButton('➖ Витрата (-)', callback_data='op_minus'),
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f'Менюшка: {category}\nОберіть тип операції:',
        reply_markup=markup,
    )

  elif call.data.startswith('op_'):
    op_type = '+' if call.data == 'op_plus' else '-'
    if user_id in user_state:
      user_state[user_id]['type'] = op_type
      user_state[user_id]['step'] = 'waiting_amount'

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='✍️ Введіть суму та опис через пробіл\nНаприклад: 1500 Купівля'
        ' деталей або просто 500:',
    )


if __name__ == '__main__':
  bot.infinity_polling()
