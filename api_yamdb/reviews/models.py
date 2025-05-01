from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from datetime import datetime

User = get_user_model()

"""Константы"""
RETURN_TEXT_LEN = 15  # Максимальная длина текста для __str__
MIN_SCORE = 1  # Минимальная оценка произведения
MAX_SCORE = 10  # Максимальная оценка произведения
MAX_LENGTH_NAME = 256  # Максимальная длина поля name
MAX_LENGTH_SLUG = 50  # Максимальная длина поля slug

def validate(value):
    year = datetime.today().year
    if value > year:
        raise ValidationError('Введенное значение, превышает текущую дату')


class BaseModel(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        max_length=MAX_LENGTH_SLUG,
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:RETURN_TEXT_LEN]


class Category(BaseModel):

    class Meta(BaseModel.Meta):
        verbose_name = 'категория'


class Genre(BaseModel):

    class Meta(BaseModel.Meta):
        verbose_name = 'жанр'


class Title(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанры'
    )
    description = models.TextField(verbose_name='Описание', blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='titles',
        verbose_name='Категории'
    )
    year = models.IntegerField(
        verbose_name='Год выпуска',
        validators=(validate,)
    )

    class Meta:
        ordering = ('-year', 'name')
        verbose_name = 'произведение'

    def __str__(self):
        return self.name[:RETURN_TEXT_LEN]


class Review(models.Model):
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews', verbose_name='Автор')
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews',
                              verbose_name='Произведение')
    score = models.IntegerField('Оценка произведения',
                                validators=[MinValueValidator(MIN_SCORE),
                                            MaxValueValidator(MAX_SCORE)])
    pub_date = models.DateTimeField('Дата пуликации', auto_now_add=True)

    class Meta:
        verbose_name = 'отзыв'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_title_author'
            ),
        )

    def __str__(self):
        return self.text[:RETURN_TEXT_LEN]


class Comment(models.Model):
    text = models.TextField('Текст')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments', verbose_name='Автор')
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Отзыв')
    pub_date = models.DateTimeField('Дата пуликации', auto_now_add=True)

    class Meta:
        verbose_name = 'комментарий'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:RETURN_TEXT_LEN]
