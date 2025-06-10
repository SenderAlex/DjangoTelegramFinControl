from datetime import datetime, timedelta
from aiogram import Bot
from asgiref.sync import sync_to_async
import pandas as pd
from utils import get_user_transactions_async
from config import TOKEN
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fincontrol_project.settings')
django.setup()

from registration_app.models import CustomUser


bot = Bot(token=TOKEN)


async def send_daily_summary():
    yesterday = datetime.now().date() - timedelta(days=1)
    start_date = yesterday
    end_date = yesterday

    users = await sync_to_async(list)(CustomUser.objects.all())
    for user in users:
        transactions = await get_user_transactions_async(user)
        if not transactions:
            continue

        data = {
            'date': [transaction.date for transaction in transactions],
            'amount': [transaction.amount for transaction in transactions],
            'type': [transaction.type for transaction in transactions],
        }
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date']).dt.date

        # Фильтруем по вчерашнему дню
        df_day = df[(df['date'] == yesterday)]

        income_sum = df_day[df_day['type'] == 'income']['amount'].sum()
        expense_sum = df_day[df_day['type'] == 'expense']['amount'].sum()

        text = (f"Добрый день!\n"
                f"За вчерашний день вы заработали: {income_sum}.\n"
                f"Потратили: {expense_sum}.")

        try:
            await bot.send_message(user.telegram_id, text)
        except Exception as e:
            # Логируйте ошибки, например, если пользователь заблокировал бота
            print(f"Не удалось отправить сообщение пользователю {user.telegram_id}: {e}")
