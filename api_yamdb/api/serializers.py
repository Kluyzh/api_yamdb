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
    # title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)

    def validate_score(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError('Score must be from 1 to 10')
        return value


class CommentSerializer(DefaultCurrentUser):
    # review = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
