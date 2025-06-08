import asyncio
import logging
import os
import django
from aiogram import Bot, Dispatcher, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram import types
from aiogram.types.input_file import FSInputFile
from config import TOKEN
from asgiref.sync import sync_to_async
import matplotlib.pyplot as plt
import pandas as pd


# Путь к настройкам вашего Django-проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fincontrol_project.settings')
django.setup()

from registration_app.models import CustomUser
from fincontrol_app.models import Transaction

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


button_registr = KeyboardButton(text="Регистрация")
button_voice_data = KeyboardButton(text="Голосовой ввод данных")
button_statistics_income = KeyboardButton(text="Статистика по доходам")
button_statistics_expense = KeyboardButton(text="Статистика по расходам")
button_hist_income = KeyboardButton(text="Гистограмма по доходам")
button_hist_expense = KeyboardButton(text="Гистограмма по расходам")
button_category_plots_income = KeyboardButton(text="Графики доходов по категориям")
button_category_plots_expense = KeyboardButton(text="Графики расходов по категориям")
button_category_hist_income = KeyboardButton(text="Гистограмма доходов по категориям")
button_category_hist_expense = KeyboardButton(text="Гистограмма расходов по категориям")


keyboards = ReplyKeyboardMarkup(keyboard=[
    [button_registr, button_voice_data],
    [button_statistics_income, button_statistics_expense, button_hist_income, button_hist_expense],
    [button_category_plots_income, button_category_plots_expense, button_category_hist_income,
     button_category_hist_expense],
    ], resize_keyboard=True)


class User(StatesGroup):
    email = State()


class RegistrationUser(StatesGroup):
    email = State()
    first_name = State()
    last_name = State()
    password = State()


class PeriodSelection(StatesGroup):
    waiting_for_start_date = State()
    waiting_for_end_date = State()


@sync_to_async
def get_telegram_id(telegram_id: int):
    try:
        return CustomUser.objects.get(telegram_id=telegram_id)
    except CustomUser.DoesNotExist:
        return None


@sync_to_async
def get_telegram_id_by_email(email: str):
    try:
        return CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return None


@sync_to_async
def update_telegram_id(user, telegram_id):
    user.telegram_id = telegram_id
    user.save()


@sync_to_async
def create_user(email, first_name, last_name, telegram_id, password):
    user = CustomUser(
        email=email,
        first_name=first_name,
        last_name=last_name,
        telegram_id=telegram_id,
    )
    user.set_password(password)  # нужно устанавливать пароль с хешированием
    user.save()
    return user


@sync_to_async
def get_user_transactions_async(user):
    return list(Transaction.objects.filter(user=user).select_related('category').order_by('-date'))


def plot_pie(data, title):
    plt.figure(figsize=(6, 6))
    data.plot.pie(autopct='%1.1f%%', startangle=90)
    plt.title(title)
    plt.axis('equal')
    file_path = f'{title}.png'
    plt.tight_layout()
    plt.savefig(file_path, format='png')
    plt.close()
    return file_path


def plot_bar(data, title, xlabel, ylabel):
    plt.figure(figsize=(8, 11))
    data.plot.bar()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis='y')
    file_path = f'{title}.png'
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()
    return file_path


def plot_category_bar(data, title, xlabel, ylabel):
    plt.figure(figsize=(8, 11))
    data.plot.bar()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(title='Категории', bbox_to_anchor=(1.05, 1), loc='upper left')
    file_path = f'{title}.png'
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()
    return file_path


@dp.message(Command('start'))
async def send_start(message: Message):
    await message.answer("Привет! Я твой помощник по учету финансов")
    await message.answer("Нажми на кнопку 'Регистрация', для получения опций по учету финансов", reply_markup=keyboards)


@dp.message(F.text == "Регистрация")
async def send_start(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    telegram_db = await get_telegram_id(telegram_id)
    if telegram_db:
        await message.answer("Вы уже зарегистрированы.")
    else:
        await state.set_state(User.email)
        await message.answer('Введите Ваш email')


@dp.message(User.email)
async def get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    data = await state.get_data()
    telegram_id = message.from_user.id
    email_from_user = data['email']
    user = await get_telegram_id_by_email(email_from_user)

    if user:
        await update_telegram_id(user, telegram_id)
        await message.answer("Ваш телеграм аккаунт успешно сохранен в базу")
    else:
        await message.answer("Пользователь с таким именем не найден!!")
        await message.answer("Вам нужно зарегистрироваться, чтобы пользоваться этим ботом.")
        await state.set_state(RegistrationUser.email)
        await state.update_data(email=email_from_user)
        await state.set_state(RegistrationUser.first_name)
        await message.answer('Введите свое имя')


@dp.message(RegistrationUser.first_name)
async def registration_user(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(RegistrationUser.last_name)
    await message.answer('Введите свою фамилию')


@dp.message(RegistrationUser.last_name)
async def registration_user(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(RegistrationUser.password)
    await message.answer('Введите пароль для своего аккаунта')


@dp.message(RegistrationUser.password)
async def registration_user(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    email = data['email']
    first_name = data['first_name']
    last_name = data['last_name']
    telegram_id = message.from_user.id
    password = data['password']
    user = await create_user(email, first_name, last_name, telegram_id, password)
    await message.answer(f'Пользователь с именем {first_name} успешно зарегистрирован')
    await state.clear()


@dp.message(F.text == "Статистика по доходам")
async def send_start(message: Message):
    user_telegram_id = message.from_user.id
    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    if not transactions:
        await message.answer("У вас нет транзакций.")
        return

    income_count = 0
    response = "Ваши транзакции по доходам:\n"
    for transaction in transactions:
        if transaction.type == 'income':
            income_count += 1
            response += (f" {income_count}. {transaction.type}: {transaction.amount} {transaction.category.name} на "
                         f"{transaction.date.strftime('%Y-%m-%d %H:%M')}\n")

    await message.answer(response)


@dp.message(F.text == "Статистика по расходам")
async def send_start(message: Message):
    user_telegram_id = message.from_user.id
    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    if not transactions:
        await message.answer("У вас нет транзакций.")
        return

    expense_count = 0
    response = "Ваши транзакции по расходам:\n"
    for transaction in transactions:
        if transaction.type == 'expense':
            expense_count += 1
            response += (f" {expense_count}. {transaction.type}: {transaction.amount} {transaction.category.name} на "
                         f"{transaction.date.strftime('%Y-%m-%d %H:%M')}\n")

    await message.answer(response)


@dp.message(F.text == "Гистограмма по доходам")
async def income_plots(message: types.Message):
    user_telegram_id = message.from_user.id
    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    # Подготовка данных
    data = {
        'date': [transaction.date.date() for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
    }

    df = pd.DataFrame(data)

    # Группировка данных и суммирование по датам
    daily_income_sums = df[df['type'] == 'income'].groupby('date')['amount'].sum()
    daily_income_values = pd.to_numeric(daily_income_sums, errors='coerce').dropna()
    daily_income_values_bar = plot_bar(daily_income_values, 'Суммы транзакций (доходов) по датам', 'Дата', 'Сумма')

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Путь к файлу с фото в той же папке
    photo_path_expense_bar = os.path.join(base_dir, daily_income_values_bar)  # замените your_photo.png на имя вашего файла

    photo_expense_bar = FSInputFile(photo_path_expense_bar)
    await message.answer_photo(photo=photo_expense_bar)


@dp.message(F.text == "Гистограмма по расходам")
async def expense_plots(message: types.Message):
    user_telegram_id = message.from_user.id
    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    # Подготовка данных
    data = {
        'date': [transaction.date.date() for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
    }

    df = pd.DataFrame(data)

    # Группировка данных и суммирование по датам
    daily_expense_sums = df[df['type'] == 'expense'].groupby('date')['amount'].sum()
    daily_expense_values = pd.to_numeric(daily_expense_sums, errors='coerce').dropna()
    daily_expense_values_bar = plot_bar(daily_expense_values, 'Суммы транзакций (расходов) по датам', 'Дата', 'Сумма')

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Путь к файлу с фото в той же папке
    photo_path_expense_bar = os.path.join(base_dir, daily_expense_values_bar)  # замените your_photo.png на имя вашего файла

    photo_expense_bar = FSInputFile(photo_path_expense_bar)
    await message.answer_photo(photo=photo_expense_bar)


@dp.message(F.text == "Графики доходов по категориям")
async def send_start(message: types.Message):
    user_telegram_id = message.from_user.id
    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    # Подготовка данных
    data = {
        'date': [transaction.date.date() for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
        'category__name': [transaction.category.name for transaction in transactions]
    }
    df = pd.DataFrame(data)

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    income_cat = df[df['type'] == 'income'].groupby('category__name')['amount'].sum()
    income_cat = pd.to_numeric(income_cat, errors='coerce').dropna()
    income_cat.name = None

    img_income_pie = plot_pie(income_cat, 'Доходы (круговая диаграмма)') if not income_cat.empty else None
    photo_path_income = os.path.join(base_dir, img_income_pie)
    photo_income = FSInputFile(photo_path_income)
    await message.answer_photo(photo=photo_income)


@dp.message(F.text == "Графики расходов по категориям")
async def send_start(message: types.Message):
    user_telegram_id = message.from_user.id
    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    # Подготовка данных
    data = {
        'date': [transaction.date.date() for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
        'category__name': [transaction.category.name for transaction in transactions]
    }
    df = pd.DataFrame(data)

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    expense_cat = df[df['type'] == 'expense'].groupby('category__name')['amount'].sum()
    expense_cat = pd.to_numeric(expense_cat, errors='coerce').dropna()
    expense_cat.name = None

    img_expense_pie = plot_pie(expense_cat, 'Расходы (круговая диаграмма)') if not expense_cat.empty else None
    photo_path_expense = os.path.join(base_dir, img_expense_pie)
    photo_expense = FSInputFile(photo_path_expense)
    await message.answer_photo(photo=photo_expense)


@dp.message(F.text == "Гистограмма доходов по категориям")
async def send_start(message: types.Message):
    user_telegram_id = message.from_user.id
    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    # Подготовка данных
    data = {
        'date': [transaction.date.date() for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
        'category__name': [transaction.category.name for transaction in transactions]
    }
    df = pd.DataFrame(data)

    income_cat_date = df[df['type'] == 'income'].pivot_table(
        index='date', columns='category__name', values='amount', aggfunc='sum', fill_value=0)
    income_cat_date = income_cat_date.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    img_cat_income_hist = plot_category_bar(income_cat_date, 'Доходы по категориям в разрезе дней', 'Дата', 'Сумма')\
        if not income_cat_date.empty else None
    photo_path_cat_income = os.path.join(base_dir, img_cat_income_hist)
    photo_cat_income = FSInputFile(photo_path_cat_income)
    await message.answer_photo(photo=photo_cat_income)


@dp.message(F.text == "Гистограмма расходов по категориям")
async def send_start(message: types.Message):
    user_telegram_id = message.from_user.id
    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    # Подготовка данных
    data = {
        'date': [transaction.date.date() for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
        'category__name': [transaction.category.name for transaction in transactions]
    }
    df = pd.DataFrame(data)

    income_cat_date = df[df['type'] == 'expense'].pivot_table(
        index='date', columns='category__name', values='amount', aggfunc='sum', fill_value=0)
    income_cat_date = income_cat_date.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    img_cat_income_hist = plot_category_bar(income_cat_date, 'Расходы по категориям в разрезе дней', 'Дата', 'Сумма')\
        if not income_cat_date.empty else None
    photo_path_cat_income = os.path.join(base_dir, img_cat_income_hist)
    photo_cat_income = FSInputFile(photo_path_cat_income)
    await message.answer_photo(photo=photo_cat_income)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
