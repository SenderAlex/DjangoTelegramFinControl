from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Уникальное поле для email
    first_name = models.CharField(max_length=15, blank=True, null=True)
    last_name = models.CharField(max_length=15, blank=True, null=True)
    date = models.DateTimeField(default=now)

    USERNAME_FIELD = 'email'  # Указываем, что уникальным полем будет email
    REQUIRED_FIELDS = ['username']  # Если есть поля, которые должны быть обязательными, укажите их здесь

    def save(self, *args, **kwargs):
        if not self.username:  # Если username пустой
            self.username = self.email  # Присваиваем значение email
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} | {self.last_name} | {self.email} | {self.date}'

    class Meta:
        ordering = ['-date']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
