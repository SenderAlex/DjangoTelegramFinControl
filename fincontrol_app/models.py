from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=64)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # on_delete=models.CASCADE  --
    # если пользователь будет удалён, все его категории и транзакции тоже автоматически удалятся.

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        def __str__(self):
            return self.name


class Transaction(models.Model):
    TYPE_CHOICES = (('income', 'Доход'), ('expenses', 'Расходы'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # decimal_places=2 -- количество цифр после запятой
    date = models.DateField()
    type = models.CharField('Тип', choices=TYPE_CHOICES, max_length=8)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)  # on_delete=models.SET_NULL -- если
    # пользователь удаляет категорию, то связанные с ней объекты не удаляются, а их поле ForeignKey у них становится
    # равным NULL
    description = models.TextField(blank=True)  # blank=True -- поле необязательное для заполнения
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

        def __str__(self):
            return f'{self.type} -- {self.amount}'
