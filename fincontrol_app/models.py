from django.db import models
from django.utils.timezone import now


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TRANSACTION_TYPES = (('income', 'Доход'), ('expense', 'Расход'))  # может быть и [], и ()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # on_delete=models.CASCADE  -- если пользователь
    # будет удалён, все его категории и транзакции тоже автоматически удалятся.

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)  # blank=True -- поле необязательное для заполнения
    date = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return f"{self.type}: {self.amount} ({self.category})"

