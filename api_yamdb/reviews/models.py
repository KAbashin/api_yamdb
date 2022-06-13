from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICE = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin')
    ]

    username = models.CharField(
        'Никнейм',
        max_length=150,
        unique=True,
        help_text='Обязательное поле, только цифры, буквы или @/./+/-/_.'
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
        null=True
    )
    email = models.EmailField(
        verbose_name='email address',
        unique=True,
        max_length=254)
    bio = models.TextField(
        'О себе',
        max_length=400,
        blank=True,
        null=True
    )
    role = models.CharField(
        'Роль',
        choices=ROLE_CHOICE,
        default=USER,
        max_length=9
    )

    class Meta:
        ordering = ["date_joined"]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}: {self.email}, уровень доступа: {self.role}'

    @property
    def is_admin(self):
        if self.role == 'admin' or self.is_superuser:
            return True
        return False

    @property
    def is_moderator(self):
        if self.role == 'moderator':
            return True
        return False

    @property
    def is_user(self):
        if self.role == 'user':
            return True
        return False
