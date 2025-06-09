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


bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(registration_router)
dp.include_router(plot_router)
dp.include_router(voice_input_router)
logging.basicConfig(level=logging.INFO)


@dp.message(Command('start'))
async def send_start(message: Message):
    await message.answer("Привет! Я твой помощник по учету финансов")
    await message.answer("Нажми на кнопку 'Регистрация', для получения опций по учету финансов", reply_markup=keyboards)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
