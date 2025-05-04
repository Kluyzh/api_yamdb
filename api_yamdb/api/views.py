from django.contrib.auth import get_user_model
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from api.base import BaseViewSet
from api.filters import TitleFilter
from api.permissions import (
    IsAdminUser,
    IsReadOnlyOrAdmin,
    IsAuthorOrModerator,
)
from api.serializers import (
    TitleSerializerRead,
    TitleSerializerWrite,
    CategorySerializer,
    GenreSerializer,
    ReviewSerializer,
    CommentSerializer,
    UserSerializer,
    UserSignupSerializer,
    TokenSerializer,
)
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class CategoryViewSet(BaseViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseViewSet):

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

    def get_queryset(self):
        return self.review.comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.review
        )


class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModerator,)
    http_method_names = (
        'get', 'post', 'patch', 'delete',
        'head', 'options', 'trace'
    )

    @property
    def get_title(self):
        return get_object_or_404(
            Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.title.reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.title)


class SignupView(APIView):

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):

    def post(self, request):
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['patch', 'get', 'post', 'delete']

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        data = request.data.copy()
        data.pop('role', None)
        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)
