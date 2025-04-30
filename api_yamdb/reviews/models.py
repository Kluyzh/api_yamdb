from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Review(models.Model):
    title = models.IntegerField()
    # title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='reviews')
    author = models.IntegerField()
    # author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    score = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(1, 'Score can\'t be lesser than 1'),
            MaxValueValidator(10, 'Score can\'t be bigger than 10'),
        )
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-pub_date', 'author',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.IntegerField()
    # review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    author = models.IntegerField()
    # author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-pub_date', 'author',)

    def __str__(self):
        return self.text
