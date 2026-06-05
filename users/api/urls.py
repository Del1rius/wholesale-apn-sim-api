from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from users.api.views import (
    UserRegistrationView,
    LoginView,
    CurrentUserView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
]
