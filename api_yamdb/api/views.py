from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from api.base import BaseViewSet
from api.filters import TitleFilter
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewCommentSerializer,
                             TitleSerializerRead, TitleSerializerWrite)
from reviews.models import Category, Genre, Review, Title
from users.permissions import IsAuthorOrModerator, IsReadOnlyOrAdmin

User = get_user_model()


class CategoryViewSet(BaseViewSet):
    permission_classes = (IsReadOnlyOrAdmin,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseViewSet):
    permission_classes = (IsReadOnlyOrAdmin,)
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')).order_by(*Title._meta.ordering)
    permission_classes = (IsReadOnlyOrAdmin,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TitleFilter
    http_method_names = (
        'get', 'post', 'patch', 'delete', 'head', 'options', 'trace'
    )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleSerializerRead
        return TitleSerializerWrite


class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModerator,)
    http_method_names = (
        'get', 'post', 'patch', 'delete',
        'head', 'options', 'trace'
    )

    @property
    def review(self):
        return get_object_or_404(
            Review.objects.select_related('title').filter(
                pk=self.kwargs.get('review_id'),
                title=self.kwargs.get('title_id')
            )
        )

    def get_queryset(self):
        return self.review.comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.review
        )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewCommentSerializer
    permission_classes = (IsAuthorOrModerator,)
    http_method_names = (
        'get', 'post', 'patch', 'delete', 'head', 'options', 'trace'
    )

    @property
    def title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.title.reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.title)
