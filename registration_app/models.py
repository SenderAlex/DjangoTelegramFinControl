from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Уникальное поле для email
    first_name = models.CharField(max_length=15, blank=True, null=True)
    last_name = models.CharField(max_length=15, blank=True, null=True)

    USERNAME_FIELD = 'email'  # Указываем, что уникальным полем будет email
    REQUIRED_FIELDS = []  # Если есть поля, которые должны быть обязательными, укажите их здесь

    # # Переопределяем поля groups и user_permissions с новым related_name
    # groups = models.ManyToManyField(
    #     Group,
    #     related_name='customuser_set',  # уникальное имя
    #     blank=True,
    #     help_text='The groups this user belongs to.'
    # )
    # user_permissions = models.ManyToManyField(
    #     Permission,
    #     related_name='customuser_permissions',  # уникальное имя
    #     blank=True,
    #     help_text='Specific permissions for this user.'
    # )

    def save(self, *args, **kwargs):
        if not self.username:  # Если username пустой
            self.username = self.email  # Присваиваем значение email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
