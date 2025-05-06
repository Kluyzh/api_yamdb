from smtplib import SMTPDataError

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api.base import BaseViewSet
from api.filters import TitleFilter
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewCommentSerializer,
                             TitleSerializerRead, TitleSerializerWrite,
                             UserSerializer)
from reviews.models import Category, Genre, Review, Title
from users.permissions import (IsAdminRolePermission, IsAuthorOrModerator,
                               IsReadOnlyOrAdmin)

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
    queryset = Title.objects.annotate(
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
            Review, pk=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id'))

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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by('id')
    serializer_class = UserSerializer
    permission_classes = (IsAdminRolePermission,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            url_name='current_user', permission_classes=(IsAuthenticated,))
    def get_me(self, request):
        user = request.user
        if request.method == 'get':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            data = request.data.copy()
            data.pop('role', None)
            serializer = self.get_serializer(user, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


class SignUpUserView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return self.send_confirmation_code(user)

        if User.objects.filter(
            username=request.data.get('username'),
            email=request.data.get('email')
        ).exists():
            user = User.objects.get(
                email=request.data.get('email')
            )
            return self.send_confirmation_code(user)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def send_confirmation_code(self, user):
        serializer = UserSerializer(user)
        confirmation_code = default_token_generator.make_token(user)
        try:
            send_mail(
                'Код подтверждения:',
                f'{confirmation_code}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
        except SMTPDataError as e:
            print(f"Ошибка отправки email: {e}")
        return Response({
            'username': serializer.data['username'],
            'email': serializer.data['email']
        }, status=status.HTTP_200_OK
        )


class JWTTokenView(TokenObtainPairView):

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        errors = {}
        if not username:
            errors['username'] = ['Обязательное поле.']
        if not confirmation_code:
            errors['confirmation_code'] = ['Обязательное поле.']
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                {'error': 'Неверный код подтверждения!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {'token': str(refresh.access_token)},
            status=status.HTTP_200_OK
        )
