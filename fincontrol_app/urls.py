from django.urls import path
from .views import transaction_list, add_transaction

urlpatterns = [
    path('list/', transaction_list, name='transaction_list'),
    path('add/', add_transaction, name='add_transaction'),
]
