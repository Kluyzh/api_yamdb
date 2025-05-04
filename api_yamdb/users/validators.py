from django.core.exceptions import ValidationError


def username_is_not_me(value):
    if value.lower() == 'me':
        raise ValidationError('Логин me запрещён')
    return value
