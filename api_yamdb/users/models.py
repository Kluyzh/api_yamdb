from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models, transaction

from .constants import (MAX_CODE_LENGTH, MAX_EMAIL_LENGTH, MAX_NAME_LENGTH,
                        MAX_ROLE_LENGTH)
from .validators import username_is_not_me


class RoleChoice(models.TextChoices):
    USER = 'user', 'Пользователь'
    MODERATOR = 'moderator', 'Модератор'
    ADMIN = 'admin', 'Администратор'


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Обязательное поле')
        try:
            with transaction.atomic():
                user = self.model(email=email, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except ValidationError:
            raise ValueError('Невозможно создать пользователя')

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', RoleChoice.USER)
        return self._create_user(email, password, **extra_fields)

    def create_moderator(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', RoleChoice.MODERATOR)
        return self._create_user(email, password, **extra_fields)

    def create_admin(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', RoleChoice.ADMIN)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', RoleChoice.ADMIN)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(
        'username',
        blank=False,
        max_length=MAX_NAME_LENGTH,
        unique=True,
        help_text=('Required. 150 characters or fewer. '
                   'Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': ("A user with that username already exists."),
        },
        validators=(username_is_not_me, UnicodeUsernameValidator())
    )
    email = models.EmailField(
        'email address',
        blank=False,
        max_length=MAX_EMAIL_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_NAME_LENGTH,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_NAME_LENGTH,
        blank=True,
        null=True
    )
    bio = models.TextField('Биография', blank=True, null=True)
    role = models.CharField(
        'Роль',
        max_length=MAX_ROLE_LENGTH,
        choices=RoleChoice.choices,
        default=RoleChoice.USER
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=MAX_CODE_LENGTH,
        blank=True,
        null=True
    )

    objects = UserManager()

    @property
    def is_admin(self):
        return self.is_superuser or self.role == RoleChoice.ADMIN.value

    @property
    def is_moderator(self):
        return self.is_staff or self.role == RoleChoice.MODERATOR.value

    @property
    def is_user(self):
        return self.role == RoleChoice.USER.value

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
