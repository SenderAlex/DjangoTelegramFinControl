from django.shortcuts import render, redirect
from .models import Transaction
from .forms import TransactionForm
from django.contrib.auth.decorators import login_required  # ограничение доступа к функциям для зарегистрированных пользователей
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO  # ???
import base64  # ????
from django.http import HttpResponse


@login_required
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    return render(request, 'fincontrol_app/transaction_list.html', {'transactions': transactions})


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            form.save()
            return redirect('fincontrol_app:transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'fincontrol_app/transaction_form.html', {'form': form})


@login_required
def show_plots(request):
    user = request.user
    qs = Transaction.objects.filter(user=user, type='expense').values('category__name', 'amount')
    df = pd.DataFrame(qs)
    if df.empty:
        return None
    else:
        df = df.groupby('category__name')['amount'].sum()
        df = pd.to_numeric(df, errors='coerce').dropna()  # errors='coerce' -- если не число, то NaN, dropna() удаляет NaN
        plt.figure(figsize=(6, 6))
        df.plot.pie(autopct='%1.1f%%')  # круговая диаграмма
        plt.title('Расходы по категориям')
        buf = BytesIO()  # создаёт буфер в памяти для временного хранения изображения.
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)  # ???перемещает указатель буфера в начало, чтобы читать данные с начала
        img = base64.b64encode(buf.read()).decode()

    return render(request, 'fincontrol_app/show_plots.html', {'img': img})

@login_required
def report_to_excel(request):
    if request.method != 'POST':
        return HttpResponse('Только POST запросы', status=405)
    user = request.user
    qs = Transaction.objects.filter(user=user, type='expense').values('category__name', 'amount')
    df = pd.DataFrame(qs)
    if df.empty:
        return HttpResponse('Нет данных для отчета', content_type="text/plain")

    df_grouped = df.groupby('category__name')['amount'].sum()
    df_grouped = pd.to_numeric(df_grouped, errors='coerce').dropna()

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:  # библиотека xlsxwriter для создания Excel-файла.
        workbook = writer.book
        worksheet = workbook.add_worksheet('Расходы по категориям')
        fig, ax = plt.subplots(figsize=(6, 6))  # cоздаёт новую фигуру (fig) и ось (ax) для построения графика matplotlib
        df_grouped.plot.pie(autopct="%1.1f%%", ax=ax)  # отображает процентное значение с точностью до одного знака после запятой на каждом секторе
        ax.set_title(f'Расходы по категориям')

        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        worksheet.insert_image('E2', 'pie.png', {'image_data': buf})
        df_grouped.to_excel(writer, sheet_name='Расходы по категориям', startrow=20)

    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=report.xlsx'
    return response





