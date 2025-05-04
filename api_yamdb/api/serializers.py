from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import User

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
