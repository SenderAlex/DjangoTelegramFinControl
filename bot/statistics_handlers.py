from aiogram import Router, F
from aiogram.types import Message
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext
from states import User, RegistrationUser  # Импортируйте ваши состояния
from utils import get_user_transactions_async # Импортируйте функции работы с БД
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fincontrol_project.settings')
django.setup()

from registration_app.models import CustomUser


router = Router()

@router.message(F.text == "Статистика по доходам")
async def income_statistics(message: Message):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

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


@router.message(F.text == "Статистика по расходам")
async def expense_statistics(message: Message):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

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