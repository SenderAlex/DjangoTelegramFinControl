from aiogram import Router, F, types
from asgiref.sync import sync_to_async
from aiogram.types.input_file import FSInputFile
from utils import get_user_transactions_async  # Импортируйте функции работы с БД
import os
import pandas as pd
from plot_utils import plot_pie, plot_bar, plot_category_bar
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fincontrol_project.settings')
django.setup()
from registration_app.models import CustomUser

router = Router()


@router.message(F.text == "Гистограмма по доходам")
async def income_plots(message: types.Message):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

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
    daily_income_sums = pd.to_numeric(daily_income_sums, errors='coerce').dropna()

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Путь к файлу с фото в той же папке
    if not daily_income_sums.empty:
        daily_income_values_bar = plot_bar(daily_income_sums, 'Суммы транзакций (доходов) по датам', 'Дата', 'Сумма')
        photo_path_income_bar = os.path.join(base_dir, daily_income_values_bar)  # замените your_photo.png на имя вашего файла
        photo_income_bar = FSInputFile(photo_path_income_bar)
        await message.answer_photo(photo=photo_income_bar)
        os.remove(daily_income_values_bar)
    else:
        await message.answer("Нет данных по доходам для построения гистограмм.")


@router.message(F.text == "Гистограмма по расходам")
async def expense_plots(message: types.Message):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

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
    daily_expense_sums = pd.to_numeric(daily_expense_sums, errors='coerce').dropna()

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Путь к файлу с фото в той же папке
    if not daily_expense_sums.empty:
        daily_expense_values_bar = plot_bar(daily_expense_sums, 'Суммы транзакций (расходов) по датам', 'Дата', 'Сумма')
        photo_path_expense_bar = os.path.join(base_dir, daily_expense_values_bar)  # замените your_photo.png на имя вашего файла
        photo_expense_bar = FSInputFile(photo_path_expense_bar)
        await message.answer_photo(photo=photo_expense_bar)
        os.remove(daily_expense_values_bar)
    else:
        await message.answer("Нет данных по расходам для построения гистограмм.")


@router.message(F.text == "Графики доходов по категориям")
async def income_cat_plots(message: types.Message):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

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

    if not income_cat.empty:
        img_income_pie = plot_pie(income_cat, 'Доходы (круговая диаграмма)') if not income_cat.empty else None
        photo_path_income = os.path.join(base_dir, img_income_pie)
        photo_income = FSInputFile(photo_path_income)
        await message.answer_photo(photo=photo_income)
        os.remove(img_income_pie)
    else:
        await message.answer("Нет данных по доходам для построения графика.")


@router.message(F.text == "Графики расходов по категориям")
async def expense_cat_plots(message: types.Message):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

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

    if not expense_cat.empty:
        img_expense_pie = plot_pie(expense_cat, 'Расходы (круговая диаграмма)') if not expense_cat.empty else None
        photo_path_expense = os.path.join(base_dir, img_expense_pie)
        photo_expense = FSInputFile(photo_path_expense)
        await message.answer_photo(photo=photo_expense)
        os.remove(img_expense_pie)
    else:
        await message.answer("Нет данных по расходам для построения графика.")


@router.message(F.text == "Гистограмма доходов по категориям")
async def income_cat_hist(message: types.Message):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

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

    if not income_cat_date.empty:
        img_cat_income_hist = plot_category_bar(income_cat_date, 'Доходы по категориям в разрезе дней', 'Дата', 'Сумма')\
            if not income_cat_date.empty else None
        photo_path_cat_income = os.path.join(base_dir, img_cat_income_hist)
        photo_cat_income = FSInputFile(photo_path_cat_income)
        await message.answer_photo(photo=photo_cat_income)
        os.remove(img_cat_income_hist)
    else:
        await message.answer("Нет данных по категориальным доходам для построения графика.")


@router.message(F.text == "Гистограмма расходов по категориям")
async def expense_cat_hist(message: types.Message):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

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

    expense_cat_date = df[df['type'] == 'expense'].pivot_table(
        index='date', columns='category__name', values='amount', aggfunc='sum', fill_value=0)
    expense_cat_date = expense_cat_date.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if not expense_cat_date.empty:
        img_cat_expense_hist = plot_category_bar(expense_cat_date, 'Расходы по категориям в разрезе дней', 'Дата', 'Сумма')\
            if not expense_cat_date.empty else None
        photo_path_cat_expense = os.path.join(base_dir, img_cat_expense_hist)
        photo_cat_expense = FSInputFile(photo_path_cat_expense)
        await message.answer_photo(photo=photo_cat_expense)
        os.remove(img_cat_expense_hist)
    else:
        await message.answer("Нет данных по категориальным расходам для построения графика.")