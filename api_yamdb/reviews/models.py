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
        blank=False,
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
        verbose_name='email',
        unique=True,
        blank=False,
        null=False,
        max_length=254)
    bio = models.TextField(
        verbose_name='О себе',
        max_length=400,
        blank=True,
        null=True
    )
    role = models.CharField(
        verbose_name='Роль',
        choices=ROLE_CHOICE,
        default=USER,
        max_length=10
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    REQUIRED_FIELDS = ["email"]
    USERNAME_FIELDS = "email"

    def __str__(self):
        return f'{self.username}: {self.email}, уровень доступа: {self.role}'

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    #       if self.role == self.ADMIN or self.is_superuser:
    #           return True
    #       return False

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR
        # if self.role == self.MODERATOR:
        #     return True
        # return False

    @property
    def is_user(self):
        return self.role == self.USER
        # if self.role == self.USER:
        #     return True
        # return False
