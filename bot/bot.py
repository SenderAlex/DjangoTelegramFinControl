import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from config import TOKEN
from keaboards import keyboards
from registration_handlers import router as registration_router
from plot_handlers import router as plot_router
from voice_input_handlers import router as voice_input_router
from scheduler import send_daily_summary
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fincontrol_project.settings')  # Укажите ваш settings
django.setup()
from registration_app.models import CustomUser
from fincontrol_app.models import Transaction, Category


minsk_tz = pytz.timezone('Europe/Minsk')


bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(registration_router)
dp.include_router(plot_router)
dp.include_router(voice_input_router)
logging.basicConfig(level=logging.INFO)


scheduler = AsyncIOScheduler(timezone=minsk_tz)


async def on_startup(dispatcher):
    scheduler.add_job(send_daily_summary, 'cron', hour=7, minute=00, timezone=minsk_tz)
    scheduler.start()


@dp.message(Command('start'))
async def send_start(message: Message):
    await message.answer("Привет! Я твой помощник по учету финансов")
    await message.answer("Нажми на кнопку 'Регистрация', для получения опций по учету финансов", reply_markup=keyboards)


async def main():
    await on_startup(dp)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
