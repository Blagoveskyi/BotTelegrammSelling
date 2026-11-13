import telebot
from telebot import types
import time
import json
import os
from datetime import datetime, timedelta

bot = telebot.TeleBot('9022589142:AAHyREka5A-nOrKO4BZElxhsB7S9NM3dbsk')

ADMIN_ID = 8868992508
wallet = "+79279498622 (Арсен, Озон Банк)"
item_link = "https://example.com/tovar"
instruction_link = "https://example.com/instruction"

def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

TARIFFS = {
    'test': {'name': '🧪 Тест (10р)', 'price': 10, 'days': 0},
    'week': {'name': '📅 Неделя', 'price': 100, 'days': 7},
    'month': {'name': '📆 Месяц 🔥 ХИТ', 'price': 299, 'days': 30},
    '3months': {'name': '👑 3 Месяца', 'price': 799, 'days': 90},
    'forever': {'name': '💎 Навсегда', 'price': 1499, 'days': 99999}
}

PROMOCODES = load_json('promo.json', {"NEWCHEAT": 0.5, "SALE20": 0.2})
DB = load_json('database.json', {"total_earned": 0, "sales": 0, "users": {}})
user_choice = {}

# Функция для проверки подписки
def get_sub_status(user_id):
    user = DB['users'].get(str(user_id))
    if not user or 'sub_expires' not in user:
        return "❌ Нет активной подписки"
    
    if user['sub_expires'] == "forever":
        return "💎 Подписка: Навсегда"
    
    expire_date = datetime.strptime(user['sub_expires'], '%Y-%m-%d')
    now = datetime.now()
    if expire_date < now:
        return "❌ Подписка истекла"
    else:
        delta = (expire_date - now).days
        return f"✅ Подписка активна (осталось {delta} дн.)"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🛒 Купить софт')
    btn2 = types.KeyboardButton('👤 Профиль')
    btn3 = types.KeyboardButton('🎁 Пригласить друга')
    btn4 = types.KeyboardButton('📝 Оставить отзыв')
    btn5 = types.KeyboardButton('❓ FAQ / Помощь')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    welcome_text = (
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Тут ты можешь купить лучший софт — <b>всё в одном</b>.\n\n"
        "🔥 <b>В комплект входит:</b>\n"
        "• Аимбот (плавный)\n"
        "• ВХ\n"
        "• Фрикам\n"
        "• Меню\n"
        "• Разблокировка 120 FPS\n\n"
        "🎁 <b>Акция:</b> Промокод <code>NEWCHEAT</code> — скидка 50%!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='HTML')

@bot.message_handler(content_types=['text'])
def menu(message):
    user_id = str(message.chat.id)
    
    if message.text == '🛒 Купить софт':
        markup = types.InlineKeyboardMarkup()
        for key, t in TARIFFS.items():
            markup.add(types.InlineKeyboardButton(text=f"{t['name']} — {t['price']}р", callback_data=f'tariff_{key}'))
        bot.send_message(message.chat.id, "💎 <b>Выбери тариф:</b>", reply_markup=markup, parse_mode='HTML')
        
    elif message.text == '👤 Профиль':
        status = get_sub_status(user_id)
        ref_link = f"https://t.me/{bot.get_me().username}?start=ref_{user_id}"
        profile_text = (
            f"👤 <b>Твой профиль</b>\n\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"👑 Статус: {status}\n\n"
            f"🔗 <b>Твоя реф-ссылка:</b>\n<code>{ref_link}</code>\n"
            f"<i>Приглашай друзей и получай 10% с покупок!</i>"
        )
        bot.send_message(message.chat.id, profile_text, parse_mode='HTML')

    elif message.text == '🎁 Пригласить друга':
        ref_link = f"https://t.me/{bot.get_me().username}?start=ref_{user_id}"
        bot.send_message(message.chat.id, f"🔗 Твоя ссылка:\n<code>{ref_link}</code>", parse_mode='HTML')

    elif message.text == '❓ FAQ / Помощь':
        bot.send_message(message.chat.id, "📖 <b>FAQ:</b>\n\nБан? — играй с левого аккаунта.\nУстановка? — инструкция после оплаты.\n\n<b>Поддержка:</b> @geouf99", parse_mode='HTML')

    elif message.text == '📝 Оставить отзыв':
        msg = bot.send_message(message.chat.id, "✍️ Напиши отзыв:")
        bot.register_next_step_handler(msg, process_feedback)

    elif message.text.lower() == 'стата' and message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, f"📊 <b>Статистика:</b>\n\n💰 Заработано: {DB['total_earned']} руб.\n📦 Продаж: {DB['sales']} шт.", parse_mode='HTML')

def process_feedback(message):
    if message.text:
        bot.send_message(ADMIN_ID, f"📩 <b>Отзыв!</b>\nОт: @{message.from_user.username if message.from_user.username else message.from_user.id}\n\n{message.text}", parse_mode='HTML')
        bot.send_message(message.chat.id, "🙏 Спасибо!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('tariff_'))
def process_tariff(call):
    user_choice[call.message.chat.id] = call.data.replace('tariff_', '')
    msg = bot.send_message(call.message.chat.id, "🎁 Введи промокод или напиши <b>нет</b>:", parse_mode='HTML')
    bot.register_next_step_handler(msg, check_promo)

def check_promo(message):
    chat_id = message.chat.id
    if message.text.lower() == 'нет':
        final_price = TARIFFS[user_choice[chat_id]]['price']
        promo_used = "Без промокода"
    else:
        promo = message.text.strip().upper()
        if promo in PROMOCODES:
            final_price = int(TARIFFS[user_choice[chat_id]]['price'] * (1 - PROMOCODES[promo]))
            promo_used = f"Промокод {promo}"
            bot.send_message(chat_id, f"✅ Промокод применен! Цена: {final_price}р")
        else:
            final_price = TARIFFS[user_choice[chat_id]]['price']
            promo_used = "Неверный промо"
            bot.send_message(chat_id, f"❌ Промо неверный. Цена: {final_price}р")

    user_choice[chat_id] = {'tariff': user_choice[chat_id], 'price': final_price, 'promo': promo_used}
    
    markup = types.InlineKeyboardMarkup()
    btn_check = types.InlineKeyboardButton(text='✅ Я перевел(а)', callback_data='card_check')
    markup.add(btn_check)
    
    bot.send_message(chat_id, f"💳 <b>Тариф:</b> {TARIFFS[user_choice[chat_id]['tariff']]['name']}\n<b>К оплате:</b> {final_price}р\n<b>Реквизиты:</b> <code>{wallet}</code>", reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == 'card_check')
def card_check(call):
    chat_id = call.message.chat.id
    order_data = user_choice.get(chat_id)
    if not order_data: return

    DB['users'][str(chat_id)] = order_data
    save_json('database.json', DB)

    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="📸 <b>Отправь скриншот или фото чека сюда!</b>", parse_mode='HTML')

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    chat_id = message.chat.id
    user_id = str(chat_id)
    
    if user_id in DB['users'] and 'tariff' in DB['users'][user_id]:
        order_data = DB['users'][user_id]
        tariff_key = order_data['tariff']
        
        bot.forward_message(ADMIN_ID, chat_id, message.message_id)
        
        markup = types.InlineKeyboardMarkup()
        btn_approve = types.InlineKeyboardButton(text='✅ Подтвердить', callback_data=f'approve_{user_id}')
        btn_decline = types.InlineKeyboardButton(text='❌ Отклонить', callback_data=f'decline_{user_id}')
        markup.add(btn_approve, btn_decline)
        
        admin_text = (
            f"🔔 <b>Новая заявка на проверку!</b>\n\n"
            f"Юзер: @{message.from_user.username if message.from_user.username else 'нет юзернейма'}\n"
            f"ID: <code>{chat_id}</code>\n"
            f"Тариф: {TARIFFS[tariff_key]['name']}\n"
            f"Цена: {order_data['price']}р\n"
            f"Промо: {order_data['promo']}\n\n"
            f"Проверь чек выше и жми кнопку:"
        )
        bot.send_message(ADMIN_ID, admin_text, reply_markup=markup, parse_mode='HTML')
        
        bot.send_message(chat_id, "⏳ <b>Чек отправлен на проверку.</b>\nОжидай подтверждения.", parse_mode='HTML')
    else:
        bot.send_message(chat_id, "❌ Сначала выбери тариф и нажми 'Я оплатил(а)'.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('decline_'))
def admin_action(call):
    if call.from_user.id != ADMIN_ID: return
    
    action, user_id = call.data.split('_')
    user = DB['users'].get(user_id)
    
    if not user:
        bot.answer_callback_query(call.id, "Юзер не найден или заявка устарела.")
        return

    if action == 'approve':
        tariff_key = user['tariff']
        
        if tariff_key == 'test':
            bot.send_message(user_id, "🎉 <b>Тест оплачен!</b>\n\n🔗 Ссылка: <b>пошел нахуй</b> 😂\n\n<i>(это тестовая заглушка)</i>", parse_mode='HTML')
        else:
            days = TARIFFS[tariff_key]['days']
            if days == 99999:
                DB['users'][user_id]['sub_expires'] = "forever"
            else:
                expire_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
                DB['users'][user_id]['sub_expires'] = expire_date

            bot.send_message(user_id, f"🎉 <b>Оплата подтверждена!</b>\n\n🔗 <b>Скачать:</b> {item_link}\n📖 <b>Инструкция:</b> {instruction_link}", parse_mode='HTML')
        
        DB['total_earned'] += user['price']
        DB['sales'] += 1
        DB['users'][user_id]['tariff'] = TARIFFS[tariff_key]['name']
        save_json('database.json', DB)
        
        bot.edit_message_text(chat_id=ADMIN_ID, message_id=call.message.message_id, text=f"✅ Заявка юзера @{user_id} одобрена и товар выдан.")
        
    elif action == 'decline':
        bot.send_message(user_id, "❌ <b>Оплата отклонена.</b>\nЧек не прошел проверку. Свяжись с поддержкой: @geouf99", parse_mode='HTML')
        bot.edit_message_text(chat_id=ADMIN_ID, message_id=call.message.message_id, text=f"❌ Заявка юзера @{user_id} отклонена.")

while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(3)
