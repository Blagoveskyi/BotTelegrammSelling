import telebot
from telebot import types

bot = telebot.TeleBot('9022589142:AAHBl4cjzvaYV7xEilBfV4EdSaKR8YYpy_0')

price = 999
wallet = "+79279498622 (Арсен, Озон Банк)" 

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🛒 Купить софт')
    btn2 = types.KeyboardButton('💬 Поддержка')
    markup.add(btn1, btn2)
    
    welcome_text = (
        "👋 <b>Приветствую!</b>\n\n"
        "Здесь ты можешь приобрести нужный софт быстро и без задержек.\n"
        "Жми кнопку ниже чтобы посмотреть товар."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='HTML')

@bot.message_handler(content_types=['text'])
def menu(message):
    if message.text == '🛒 Купить софт':
        markup = types.InlineKeyboardMarkup()
        btn_pay = types.InlineKeyboardButton(text=f'✅ Я оплатил {price}р', callback_data='check_pay')
        markup.add(btn_pay)
        
        pay_text = (
            f"💳 <b>Реквизиты для оплаты:</b>\n\n"
            f"Сумма: <b>{price} рублей</b>\n"
            f"Перевод на: <code>{wallet}</code>\n\n"
            f"После перевода нажми кнопку ниже 👇"
        )
        bot.send_message(message.chat.id, pay_text, reply_markup=markup, parse_mode='HTML')
        
    elif message.text == '💬 Поддержка':
        bot.send_message(message.chat.id, '❓ По всем вопросам пиши сюда: @geouf99')

@bot.callback_query_handler(func=lambda call: call.data == 'check_pay')
def callback_inline(call):
    success_text = (
        "🎉 <b>Оплата принята!</b>\n\n"
        "Спасибо за покупку. Твой товар готов к выдаче:\n"
        "🔗 https://example.com/tovar"
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=success_text, parse_mode='HTML')

bot.infinity_polling()

