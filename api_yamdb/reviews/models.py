from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import UniqueConstraint


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
        verbose_name='email address',
        unique=True,
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
        max_length=9
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        ordering = ["date_joined"]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}: {self.email}, уровень доступа: {self.role}'

    @property
    def is_admin(self):
        if self.role == self.ADMIN or self.is_superuser:
            return True
        return False

    @property
    def is_moderator(self):
        if self.role == self.MODERATOR:
            return True
        return False

    @property
    def is_user(self):
        if self.role == self.USER:
            return True
        return False


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        UniqueConstraint(fields=['title', 'author'], name='unique_review')

    def __str__(self):
        return f'{self.title}, {self.score}, {self.author}'


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author}, {self.pub_date:%d.%m.%Y}, {self.text}'
