from django.urls import path

from .views.authentication_views import LoginView, RegisterView, TestEmailService

urlpatterns = [
    path("register/", RegisterView.as_view(), name="Register User"),
    path("login/", LoginView.as_view(), name="Login User"),
    path("test-email/", TestEmailService.as_view(), name="Test Email"),
]
