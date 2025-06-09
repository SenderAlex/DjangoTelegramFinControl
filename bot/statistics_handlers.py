from aiogram.types import Message
from asgiref.sync import sync_to_async
from utils import get_user_transactions_async # Импортируйте функции работы с БД
from keaboards import period_choice_keyboard
import pandas as pd
import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fincontrol_project.settings')
django.setup()

from registration_app.models import CustomUser


async def income_statistics(message: Message, start_date: str = None, end_date: str = None):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    if not transactions:
        await message.answer("У вас нет транзакций.")
        return

    # Подготовка данных для DataFrame
    data = {
        'date': [transaction.date for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
        'category': [transaction.category.name for transaction in transactions],
    }
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.date

    # Фильтрация по датам, если заданы
    if start_date and end_date:
        try:
            start = pd.to_datetime(start_date).date()
            end = pd.to_datetime(end_date).date()
            df = df.loc[(df['date'] >= start) & (df['date'] <= end)]
        except Exception:
            await message.answer("Ошибка в формате даты. Используйте ГГГГ-ММ-ДД.")
            return

    # Фильтруем только доходы
    df_income = df[df['type'] == 'income']

    if df_income.empty:
        await message.answer("Нет доходных транзакций за выбранный период.")
        return

    response = "Ваши транзакции по доходам:\n"
    for i, row in enumerate(df_income.itertuples(), 1):
        response += (
            f" {i}. {row.type}: {row.amount} {row.category} на "
            f"{row.date.strftime('%Y-%m-%d %H:%M')}\n"
        )

    await message.answer(response)
    await message.answer("Вывести статистику данных по доходам за выбранный период?", reply_markup=period_choice_keyboard())


async def expense_statistics(message: Message, start_date: str = None, end_date: str = None):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    if not transactions:
        await message.answer("У вас нет транзакций.")
        return

    # Подготовка данных для DataFrame
    data = {
        'date': [transaction.date for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
        'category': [transaction.category.name for transaction in transactions],
    }
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.date

    # Фильтрация по датам, если заданы
    if start_date and end_date:
        try:
            start = pd.to_datetime(start_date).date()
            end = pd.to_datetime(end_date).date()
            df = df.loc[(df['date'] >= start) & (df['date'] <= end)]
        except Exception:
            await message.answer("Ошибка в формате даты. Используйте ГГГГ-ММ-ДД.")
            return

    # Фильтруем только расходы
    df_income = df[df['type'] == 'expense']

    if df_income.empty:
        await message.answer("Нет доходных транзакций за выбранный период.")
        return

    response = "Ваши транзакции по доходам:\n"
    for i, row in enumerate(df_income.itertuples(), 1):
        response += (
            f" {i}. {row.type}: {row.amount} {row.category} на "
            f"{row.date.strftime('%Y-%m-%d %H:%M')}\n"
        )

    await message.answer(response)
    await message.answer("Вывести статистику данных по расходам за выбранный период?",
                         reply_markup=period_choice_keyboard())