from django.urls import path

from .views.authentication_views import (LoginView, PasswordResetView,
                                         RegisterView,
                                         SendResetPasswordMailView)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="Register User"),
    path("login/", LoginView.as_view(), name="Login User"),
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
]
