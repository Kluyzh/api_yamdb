from django.contrib.auth import get_user_model
from rest_framework import permissions

from .models import RoleChoice

User = get_user_model()


class IsAdminRolePermission(permissions.BasePermission):
    """
    Permission class для проверки роли ADMIN или суперпользователя.
    Позволяет доступ только пользователям с role = 'admin'
    или is_superuser = True.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
            request.user.is_superuser
            or request.user.role == RoleChoice.ADMIN
        )

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return (
                request.user.is_superuser
                or request.user.role == RoleChoice.ADMIN
                or obj == request.user
            )
        return (
            request.user.is_superuser
            or request.user.role == RoleChoice.ADMIN
        )


class IsUserAuthRolePermission(permissions.BasePermission):
    """
    Permission class для проверки роли USER.
    Позволяет доступ только пользователям с role = 'user'.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == RoleChoice.USER

    def has_object_permission(self, request, view, obj):
        return request.user.role == RoleChoice.USER


class IsModeratorRolePermission(permissions.BasePermission):
    """
    Permission class для проверки роли MODERATOR.
    Позволяет доступ только пользователям с role = 'moderator'.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == RoleChoice.MODERATOR

    def has_object_permission(self, request, view, obj):
        return request.user.role == RoleChoice.MODERATOR


class CategoryGenrePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and request.user.role == RoleChoice.ADMIN
            )
        )

class IsReadOnlyOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            (request.user.is_authenticated and request.user.role == RoleChoice.ADMIN)
            or request.method in permissions.SAFE_METHODS
        )


class IsAuthorOrModerator(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role == RoleChoice.MODERATOR
            or request.user.role == RoleChoice.ADMIN
            or request.user.is_superuser
        )