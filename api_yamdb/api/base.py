from rest_framework import filters, mixins, viewsets

from api.permissions import IsAdminOrReadOnly

from api_yamdb.api.permissions import IsReadOnlyOrAdmin


class BaseViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):

    lookup_field = 'slug'
    permission_classes = (IsReadOnlyOrAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
