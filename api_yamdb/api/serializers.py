from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.mail import send_mail

from rest_framework import serializers
from users.models import User

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.

    Преобразует объекты модели User в JSON и обратно.
    Включает поля username, first_name, last_name, email, bio, role.
    """

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'bio',
            'role',
        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializerRead(serializers.ModelSerializer):

    rating = serializers.IntegerField(read_only=True, default=None)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'genre', 'category'
        )


class TitleSerializerWrite(serializers.ModelSerializer):

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        allow_null=False,
        allow_empty=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year',
            'description', 'genre', 'category'
        )

    def to_representation(self, instance):
        return TitleSerializerRead(instance).data


class ReviewCommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'author', 'score', 'text', 'pub_date')

    def validate(self, data):
        if (
            self.context['request'].method == 'POST'
            and Review.objects.filter(
                author=self.context['request'].user,
                title=self.context['view'].kwargs.get('title_id')
            ).exists()
        ):
            raise serializers.ValidationError('Отзыв уже присутствует')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'pub_date')


class UserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')


class UserSignupSerializer(serializers.Serializer):

    username = serializers.CharField(
        required=True,
        validators=(ASCIIUsernameValidator(),)
    )
    email = serializers.EmailField(
        required=True,
    )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        if User.objects.filter(
                email=email
        ).exclude(username=username).exists():
            raise serializers.ValidationError(
                'email уже зарегистрирован'
            )

        if User.objects.filter(
                username=username
        ).exclude(email=email).exists():
            raise serializers.ValidationError(
                'username уже зарегистрирован'
            )

        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Недопустимое имя пользователя: me'
            )

        return data

    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=None,
            recipient_list=[user.email],
        )
        return user


# class TokenSerializer(serializers.Serializer):

#     username = serializers.CharField(
#         max_length=MAX_LENGTH_USERNAME,
#         required=True,
#         validators=[
#             ASCIIUsernameValidator(),
#             username_not_me
#         ]
#     )
#     confirmation_code = serializers.CharField(required=True)

#     def validate(self, data):
#         username = data.get('username')
#         confirmation_code = data.get('confirmation_code')
#         user = get_object_or_404(User, username=username)

#         if not default_token_generator.check_token(user, confirmation_code):
#             raise serializers.ValidationError('Неверный confirmation_code')

#         return {'token': str(AccessToken.for_user(user))}
