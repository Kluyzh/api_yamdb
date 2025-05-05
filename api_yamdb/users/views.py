from smtplib import SMTPDataError

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api.serializers import UserSerializer

from .permissions import IsAdminRolePermission

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by('id')
    serializer_class = UserSerializer
    permission_classes = (IsAdminRolePermission,)
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
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

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

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
