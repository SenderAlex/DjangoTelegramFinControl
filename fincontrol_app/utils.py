# finance/utils.py
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64


def plot_expense_by_category(user):
    from .models import Transaction
    qs = Transaction.objects.filter(user=user, type='expense').values('category__name', 'amount')
    df = pd.DataFrame(qs)
    if df.empty:
        return None
    df = df.groupby('category__name')['amount'].sum()
    plt.figure(figsize=(6, 6))
    df.plot.pie(autopct='%1.1f%%')
    plt.title('Расходы по категориям')
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()
