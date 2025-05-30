from django.shortcuts import render, redirect
from .models import Transaction
from .forms import TransactionForm
from django.contrib.auth.decorators import login_required  # ограничение доступа к функциям для зарегистрированных
# пользователей


@login_required
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    return render(request, 'fincontrol_app/transaction_list.html', {'transactions': transactions})


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'fincontrol_app/transaction_form.html', {'form': form})

