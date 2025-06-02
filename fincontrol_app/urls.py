from django.urls import path
from .views import transaction_list, add_transaction, show_plots, report_to_excel

app_name = 'fincontrol_app'

urlpatterns = [
    path('list/', transaction_list, name='transaction_list'),
    path('add/', add_transaction, name='add_transaction'),
    path('plot/', show_plots, name='show_plots'),
    path('excel/', report_to_excel, name='report_to_excel'),
]
