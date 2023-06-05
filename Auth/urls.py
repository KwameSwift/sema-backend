from django.urls import path

from .views.authentication_views import (ChangePasswordView, LoginView,
                                         PasswordResetView, RegisterView,
                                         SendResetPasswordMailView)
from .views.user_roles_views import (AddUserRoleView, DeleteUserRoleView,
                                     GetAllUserRolesView,
                                     GetSingleUserRoleView, UpdateUserRoleView)

urlpatterns = [
    # User authentication
    path("register/", RegisterView.as_view(), name="Register User"),
    path("login/", LoginView.as_view(), name="Login User"),
    path("change-password/", ChangePasswordView.as_view(), name="Change Password"),
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
    # User roles
    path("add-user-role/", AddUserRoleView.as_view(), name="Add User Role"),
    path(
        "delete-user-role/<int:role_id>/",
        DeleteUserRoleView.as_view(),
        name="Delete User Role",
    ),
    path(
        "get-all-user-roles/<int:page_number>/",
        GetAllUserRolesView.as_view(),
        name="Get All User Roles",
    ),
    path(
        "get-user-role/<int:role_id>/",
        GetSingleUserRoleView.as_view(),
        name="Get Single User Role",
    ),
    path(
        "update-user-role/<int:role_id>/",
        UpdateUserRoleView.as_view(),
        name="Update User Role",
    ),
]
