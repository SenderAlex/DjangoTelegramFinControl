from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction, Category
from .forms import TransactionForm
from django.contrib.auth.decorators import login_required  # ограничение доступа к функциям для зарегистрированных пользователей
from django.http import HttpResponse, JsonResponse
from django.utils.dateparse import parse_date
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO  # ???
import base64  # ????
from datetime import datetime, timedelta


@login_required
def transaction_list(request):
    # Получаем все транзакции пользователя и сортируем по дате
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    # Получаем параметры фильтра из GET-запроса
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Применяем фильтр по дате начала
    if start_date:
        transactions = transactions.filter(date__gte=start_date)

    # Применяем фильтр по дате конца
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        transactions = transactions.filter(date__lte=end_date_obj)

    # Мы хотим отображать 5 записей на страницу
    paginator = Paginator(transactions, 5)  # 5 записей на страницу

    # Получаем номер текущей страницы из GET-запроса
    page_number = request.GET.get('page')

    # Получаем объекты текущей страницы
    page_obj = paginator.get_page(page_number)

    # Передаем в контекст данных список транзакций для текущей страницы
    return render(request, 'fincontrol_app/transaction_list.html', {'page_obj': page_obj})


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

    # Получаем даты из GET-параметров, если есть
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    date_from_parsed = parse_date(date_from) if date_from else None
    date_to_parsed = parse_date(date_to) if date_to else None

    qs = Transaction.objects.filter(user=user)
    if date_from_parsed:
        qs = qs.filter(date__date__gte=date_from_parsed)
    if date_to_parsed:
        qs = qs.filter(date__date__lte=date_to_parsed)

    df = pd.DataFrame(qs.values('type', 'category__name', 'date', 'amount'))
    if df.empty:
        return HttpResponse('Нет данных для отображения')

    df['date'] = pd.to_datetime(df['date']).dt.date

    def plot_pie(data, title):
        plt.figure(figsize=(6, 6))
        data.plot.pie(autopct='%1.1f%%', startangle=90)
        plt.title(title)
        plt.axis('equal')
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()

    def plot_bar(data, title, xlabel, ylabel):
        plt.figure(figsize=(8, 11))
        data.plot.bar()
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(axis='y')
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()

    # 1,2. Доходы и расходы (круговые диаграммы)
    income_cat = df[df['type'] == 'income'].groupby('category__name')['amount'].sum()
    income_cat = pd.to_numeric(income_cat, errors='coerce').dropna()
    income_cat.name = None
    expense_cat = df[df['type'] == 'expense'].groupby('category__name')['amount'].sum()
    expense_cat = pd.to_numeric(expense_cat, errors='coerce').dropna()
    expense_cat.name = None

    img_income_pie = plot_pie(income_cat, 'Доходы (круговая диаграмма)') if not income_cat.empty else None
    img_expense_pie = plot_pie(expense_cat, 'Расходы (круговая диаграмма)') if not expense_cat.empty else None

    # 3,4. Доходы и расходы по дате (гистограммы)
    income_date = df[df['type'] == 'income'].groupby('date')['amount'].sum()
    income_date = pd.to_numeric(income_date, errors='coerce').dropna()
    expense_date = df[df['type'] == 'expense'].groupby('date')['amount'].sum()
    expense_date = pd.to_numeric(expense_date, errors='coerce').dropna()

    img_income_date_bar = plot_bar(income_date, 'Доходы по дате (гистограмма)', 'Дата', 'Сумма') if not income_date.empty else None
    img_expense_date_bar = plot_bar(expense_date, 'Расходы по дате (гистограмма)', 'Дата', 'Сумма') if not expense_date.empty else None

    # 5,6. Доходы и расходы по каждой категории по дате (гистограммы)
    # Сгруппируем по дате и категории, затем сделаем сводную таблицу
    income_cat_date = df[df['type'] == 'income'].pivot_table(
        index='date', columns='category__name', values='amount', aggfunc='sum', fill_value=0)
    income_cat_date = income_cat_date.apply(pd.to_numeric, errors='coerce').fillna(0)
    expense_cat_date = df[df['type'] == 'expense'].pivot_table(
        index='date', columns='category__name', values='amount', aggfunc='sum', fill_value=0)
    expense_cat_date = expense_cat_date.apply(pd.to_numeric, errors='coerce').fillna(0)

    img_income_cat_date_bar = None
    if not income_cat_date.empty:
        plt.figure(figsize=(8, 9))
        income_cat_date.plot(kind='bar', stacked=False)
        plt.title('Доходы по каждой категории по дате (гистограмма)')
        plt.xlabel('Дата')
        plt.ylabel('Сумма')
        plt.legend(title='Категории', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        img_income_cat_date_bar = base64.b64encode(buf.read()).decode()

    img_expense_cat_date_bar = None
    if not expense_cat_date.empty:
        plt.figure(figsize=(8, 9))
        expense_cat_date.plot(kind='bar', stacked=False)
        plt.title('Расходы по каждой категории по дате (гистограмма)')
        plt.xlabel('Дата')
        plt.ylabel('Сумма')
        plt.legend(title='Категории', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        img_expense_cat_date_bar = base64.b64encode(buf.read()).decode()

    context = {
        'img_income_pie': img_income_pie,
        'img_expense_pie': img_expense_pie,
        'img_income_date_bar': img_income_date_bar,
        'img_expense_date_bar': img_expense_date_bar,
        'img_income_cat_date_bar': img_income_cat_date_bar,
        'img_expense_cat_date_bar': img_expense_cat_date_bar,
        'date_from': date_from,
        'date_to': date_to,
    }

    return render(request, 'fincontrol_app/show_plots.html', {'context': context})


@login_required
def report_to_excel(request):
    if request.method != 'POST':
        return HttpResponse('Только POST запросы', status=405)

    user = request.user

    # Получаем даты из POST-параметров (если передаете их из формы)
    date_from = request.POST.get('date_from')
    date_to = request.POST.get('date_to')
    date_from_parsed = parse_date(date_from) if date_from else None
    date_to_parsed = parse_date(date_to) if date_to else None

    qs = Transaction.objects.filter(user=user)
    if date_from_parsed:
        qs = qs.filter(date__date__gte=date_from_parsed)
    if date_to_parsed:
        date_to_plus = date_to_parsed + timedelta(days=1)
        qs = qs.filter(date__date__lt=date_to_plus)

    df = pd.DataFrame(qs.values('type', 'category__name', 'date', 'amount'))
    if df.empty:
        return HttpResponse('Нет данных для отчета', content_type="text/plain")

    df['date'] = pd.to_datetime(df['date']).dt.date

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book

        # 1) Добавляем лист со списком транзакций (первый лист)
        df_sorted = df.sort_values(by='date', ascending=False)
        df_sorted.rename(columns={
            'type': 'Тип',
            'category__name': 'Категория',
            'date': 'Дата',
            'amount': 'Сумма',
            'description': 'Описание'
        }, inplace=True)
        df_sorted.to_excel(writer, sheet_name='Транзакции', index=False)

        def insert_plot(df_grouped, chart_title, sheet_name, startrow, startcol, chart_type='pie', stacked=False):
            worksheet = workbook.add_worksheet(sheet_name)

            # Преобразуем данные в числовой формат
            if isinstance(df_grouped, pd.DataFrame):
                df_grouped = df_grouped.apply(pd.to_numeric, errors='coerce').fillna(0)
                if df_grouped.empty or df_grouped.sum().sum() == 0:
                    return  # Нет данных — пропускаем
            else:
                df_grouped = pd.to_numeric(df_grouped, errors='coerce').dropna()
                if df_grouped.empty:
                    return  # Нет данных — пропускаем

            fig, ax = plt.subplots(figsize=(6, 6))
            if chart_type == 'pie':
                df_grouped.plot.pie(autopct='%1.1f%%', ax=ax, startangle=90)  # # отображает процентное значение с
                # точностью до одного знака после запятой на каждом секторе
            elif chart_type == 'bar':
                df_grouped.plot.bar(stacked=stacked, ax=ax)
                ax.set_xlabel('Категории' if chart_type == 'bar' else '')
                ax.set_ylabel('Сумма')
                ax.grid(True)

            ax.set_title(chart_title)

            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)

            worksheet.insert_image(startrow, startcol, 'chart.png', {'image_data': buf})
            df_grouped.to_excel(writer, sheet_name=sheet_name, startrow=startrow + 20)


        # 1) Доходы (круговая)
        income_cat = df[df['type'] == 'income'].groupby('category__name')['amount'].sum()
        income_cat.name = None
        if not income_cat.empty:
            insert_plot(income_cat, 'Доходы (круговая диаграмма)', 'Доходы по категориям',
                        1, 3, 'pie')

        # 2) Расходы (круговая)
        expense_cat = df[df['type'] == 'expense'].groupby('category__name')['amount'].sum()
        expense_cat.name = None
        if not expense_cat.empty:
            insert_plot(expense_cat, 'Расходы (круговая диаграмма)', 'Расходы по категориям',
                        1, 3, 'pie')

        # 3) Доходы по дате (гистограмма)
        income_date = df[df['type'] == 'income'].groupby('date')['amount'].sum()
        if not income_date.empty:
            insert_plot(income_date, 'Доходы по дате', 'Доходы по дате',
                        1, 3, 'bar')

        # 4) Расходы по дате (гистограмма)
        expense_date = df[df['type'] == 'expense'].groupby('date')['amount'].sum()
        if not expense_date.empty:
            insert_plot(expense_date, 'Расходы по дате', 'Расходы по дате',
                        1, 3, 'bar')

        # 5) Доходы по каждой категории по дате (гистограмма)
        income_cat_date = df[df['type'] == 'income'].pivot_table(index='date', columns='category__name',
                                                                 values='amount', aggfunc='sum').fillna(0)
        if not income_cat_date.empty:
            insert_plot(income_cat_date, 'Доходы по каждой категории по дате',
                        'Доходы по категориям и дате', 1, 4, 'bar', stacked=False)

        # 6) Расходы по каждой категории по дате (гистограмма)
        expense_cat_date = df[df['type'] == 'expense'].pivot_table(index='date', columns='category__name',
                                                                   values='amount', aggfunc='sum').fillna(0)
        if not expense_cat_date.empty:
            insert_plot(expense_cat_date, 'Расходы по каждой категории по дате',
                        'Расходы по категориям и дате', 1, 4, 'bar', stacked=False)

    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=report.xlsx'
    return response


def get_categories(request, type):  # в зависимости от типа своя категория
    categories = Category.objects.filter(type=type).values('id', 'name')
    return JsonResponse({'categories': list(categories)})


@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('fincontrol_app:transaction_list')
    else:
        form = TransactionForm(instance=transaction)
        return render(request, 'fincontrol_app/edit_transaction.html', {'form': form})

@login_required
def financial_tips(request):
    tips = [
        "Ведите учёт всех расходов и доходов.",
        "Откладывайте минимум 10% от дохода.",
        "Регулярно анализируйте траты по категориям.",
        "Ищите возможности дополнительного заработка: фриланс, инвестиции, обучение новым навыкам.",
        "Сравнивайте цены и ищите скидки перед покупкой.",
    ]
    return render (request, 'fincontrol_app/financial_tips.html', {'tips': tips})



