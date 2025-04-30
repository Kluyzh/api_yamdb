from rest_framework import serializers
from reviews.models import Review, Comment
from django.contrib.auth import get_user_model

User = get_user_model()


class DefaultCurrentUser(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )


class ReviewSerializer(DefaultCurrentUser):
    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)


class CommentSerializer(DefaultCurrentUser):
    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
