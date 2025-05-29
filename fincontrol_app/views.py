from django.views.generic import CreateView, ListView  # базовые классовые представления для создания и отображения списков объектов.
from django.urls import reverse_lazy  # отложенный вызов функции для получения URL по имени, используется в атрибутах классов
from django.contrib.auth.mixins import LoginRequiredMixin  # защищает страницы от неавторизованных пользователей, требуя входа.
from .models import Transaction
from .forms import TransactionForm


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'fincontrol_app/transaction_list.html'  # путь к шаблону
    context_object_name = 'transactions'  # 'transaction' -- переменной, которая будет доступна в шаблоне
    # для данных списка
    paginate_by = 10

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related('category')  # загружает транзакции
        # данного пользователя, связанные объекты 'category'


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    model_form = TransactionForm
    template_name = 'fincontrol_app/transaction_form.html'
    success_url = reverse_lazy('transaction-list')  # в случае успешщного заполнения пройдет перенаправление на список
    # транзакций

    def form_valid(self, form):
        form.instance.user = self.request.user  # присваивает объекту, создаваемому из формы, пользователя, который
        # отправляет форму. Это нужно, чтобы связать создаваемую транзакцию именно с этим пользователем.
        return super().form_valid(form)



