from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from .views.authentication_views import (
    CallBack,
    ChangePasswordView,
    GuestLoginView,
    LoginView,
    PasswordResetView,
    RegisterView,
    SendResetPasswordMailView,
    VerifyPasswordResetCode,
)

urlpatterns = [
    # User authentication
    path("register/", RegisterView.as_view(), name="Register User"),
    path("login/", LoginView.as_view(), name="Login User"),
    path("guest-login/", GuestLoginView.as_view(), name="Guest Login"),
    path("change-password/", ChangePasswordView.as_view(), name="Change Password"),
    path("refresh-token/", jwt_views.TokenRefreshView.as_view(), name="Refresh Token"),
    path(
        "send-reset-password-mail/",
        SendResetPasswordMailView.as_view(),
        name="Send Password Reset Mail",
    ),
    path(
        "reset-password/",
        PasswordResetView.as_view(),
        name="Reset Password",
    ),
    path(
        "verify-password-reset-code/",
        VerifyPasswordResetCode.as_view(),
        name="Verify Reset Password Code",
    ),
    path(
        "callback/",
        CallBack.as_view(),
        name="Call Back",
    ),
]
