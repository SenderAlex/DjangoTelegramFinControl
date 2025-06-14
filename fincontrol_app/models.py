from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    CATEGORY_TYPES = (
        ('income', 'Доход'),
        ('expense', 'Расход'),
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.name} {self.type}'


class SubCategory(models.Model):
    SUBCATEGORY_TYPES = (
        ('food', 'Еда'),
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=SUBCATEGORY_TYPES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

    def __str__(self):
        return self.name


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    TRANSACTION_TYPES = (('income', 'Доход'), ('expense', 'Расход'))  # может быть и [], и ()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # on_delete=models.CASCADE  -- если пользователь
    # будет удалён, все его категории и транзакции тоже автоматически удалятся.

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)  # blank=True -- поле необязательное для заполнения
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return f"{self.type}: {self.amount} ({self.category})"

