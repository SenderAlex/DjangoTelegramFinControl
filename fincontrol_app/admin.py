from django.contrib import admin
from .models import Category, Transaction, SubCategory
from .forms import TransactionForm


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    list_filter = ('type', )


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    list_filter = ('type', )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    form = TransactionForm
    list_display = ('type', 'category', 'amount', 'description', 'date')
    list_filter = ('type', 'category', )