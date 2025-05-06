from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class IsAdminRolePermission(permissions.BasePermission):
    """
    Permission class для проверки роли ADMIN или суперпользователя.
    Позволяет доступ только пользователям с role = 'admin'
    или is_superuser = True.
    """

    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_admin)

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return (request.user.is_admin or obj == request.user)
        return request.user.is_admin


class IsUserAuthRolePermission(permissions.BasePermission):
    """
    Permission class для проверки роли USER.
    Позволяет доступ только пользователям с role = 'user'.
    """

    def has_permission(self, request, view):
        return (request.user.is_user and request.user.is_authenticated)


class IsModeratorRolePermission(permissions.BasePermission):
    """
    Permission class для проверки роли MODERATOR.
    Позволяет доступ только пользователям с role = 'moderator'.
    """

    def has_permission(self, request, view):
        return (request.user.is_moderator and request.user.is_authenticated)


class IsReadOnlyOrAdmin(permissions.BasePermission):
    """
    Permission class для проверки роли Admin.
    Позволяет доступ к безопасным методам только пользователям 'admin'.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAuthorOrModerator(permissions.BasePermission):
    """
    Permission class для проверки роли Author.
    Позволяет доступ к безопасным методам только автору, админу, модератору.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
