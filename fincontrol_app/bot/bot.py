import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fincontrol_project.settings')
django.setup()

from aiogram import Bot, Dispatcher, executor, types
from fincontrol_app.models import Transaction, Category
from django.contrib.auth.models import User
from datetime import date

API_TOKEN = 'ВАШ_ТОКЕН_БОТА'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Можно реализовать регистрацию через команду /start с генерацией кода на сайте.
# Для MVP допустим, что username Telegram совпадает с username Django.
def get_user_by_telegram(message):
    try:
        return User.objects.get(username=message.from_user.username)
    except User.DoesNotExist:
        return None

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user = get_user_by_telegram(message)
    if user:
        await message.answer("Добро пожаловать! Используйте /today, /add, /week и т.д.")
    else:
        await message.answer("Пожалуйста, зарегистрируйтесь на сайте и укажите username Telegram.")

@dp.message_handler(commands=['today'])
async def cmd_today(message: types.Message):
    user = get_user_by_telegram(message)
    if not user:
        await message.answer("Пользователь не найден.")
        return
    today = date.today()
    expenses = Transaction.objects.filter(user=user, type='expense', date=today)
    total = sum(e.amount for e in expenses)
    await message.answer(f"Ваши расходы сегодня: {total} руб.")

@dp.message_handler(commands=['add'])
async def cmd_add(message: types.Message):
    await message.answer("Введите сумму, тип (доход/расход), категорию и описание через запятую.\n"
                         "Пример: 500, расход, Еда, обед")

@dp.message_handler(lambda m: ',' in m.text)
async def add_transaction_handler(message: types.Message):
    user = get_user_by_telegram(message)
    if not user:
        await message.answer("Пользователь не найден.")
        return
    try:
        amount, type_, category_name, *desc = [x.strip() for x in message.text.split(',')]
        amount = float(amount)
        category, _ = Category.objects.get_or_create(name=category_name, owner=user)
        Transaction.objects.create(
            user=user,
            amount=amount,
            date=date.today(),
            type='expense' if type_ == 'расход' else 'income',
            category=category,
            description=' '.join(desc)
        )
        await message.answer("Операция добавлена!")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
