from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import SignUpUserView, JWTTokenView, UserViewSet

app_name: str = 'api'

v1_router = DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/token/', JWTTokenView.as_view(), name='token'),
    path('v1/auth/signup/', SignUpUserView.as_view(), name='signup')
]
