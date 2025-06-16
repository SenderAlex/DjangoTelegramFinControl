import re
from asgiref.sync import sync_to_async
from registration_app.models import CustomUser
from fincontrol_app.models import Transaction, Category


def parse_transaction(text):
    text = text.lower()
    if 'доход' in text:
        type_ = 'income'
    elif 'расход' in text:
        type_ = 'expense'
    else:
        type_ = None

    amount_match = re.search(r'\d+', text)
    amount = int(amount_match.group()) if amount_match else None

    income_categories = ['зарплата', 'акции', 'криптовалюта', 'бизнес']
    expense_categories = ['еда', 'развлечения', 'спорт']

    category = None
    for cat in income_categories + expense_categories:
        if cat in text:
            category = cat
            break

    description = None
    if category:
        description_start = text.find(category) + len(category)
        description = text[description_start:].strip()

    return {
        'type': type_,
        'amount': amount,
        'category': category,
        'description': description
    }


@sync_to_async
def get_telegram_id(telegram_id: int):
    try:
        return CustomUser.objects.get(telegram_id=telegram_id)
    except CustomUser.DoesNotExist:
        return None


@sync_to_async
def create_transaction(user, type_, amount, category_name, description):
    category = Category.objects.get(name=category_name)
    transaction = Transaction(
        user=user,
        type=type_,
        amount=amount,
        category=category,
        description=description
    )
    transaction.save()
    return transaction


async def save_transaction(user_id, type_, amount, category, description):
    user = await get_telegram_id(user_id)
    transaction = await create_transaction(user, type_, amount, category, description)
    return transaction