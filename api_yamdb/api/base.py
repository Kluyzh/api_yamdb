from rest_framework import filters, mixins, viewsets

from users.permissions import IsAdminRolePermission


class BaseViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):

    lookup_field = 'slug'
    permission_classes = (IsAdminRolePermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
