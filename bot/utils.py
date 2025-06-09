from asgiref.sync import sync_to_async
import os
import django

# Путь к настройкам вашего Django-проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fincontrol_project.settings')
django.setup()

from registration_app.models import CustomUser
from fincontrol_app.models import Transaction


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