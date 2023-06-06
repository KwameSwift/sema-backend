from django.urls import path

from .views.authentication_views import (ChangePasswordView, LoginView, VerifyPasswordResetCode,
                                         PasswordResetView, RegisterView,
                                         SendResetPasswordMailView)
from .views.permissions_view import (AddUserRole, DeleteUserRole, AddModuleView,
                                     GetAllUserRoles, UpdateUserRole, GetSingleRole)

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
    path(
        "verify-password-reset-code/",
        VerifyPasswordResetCode.as_view(),
        name="Verify Reset Password Code",
    ),
    # User roles
    path("add-user-role/", AddUserRole.as_view(), name="Add User Role"),
    path(
        "delete-user-role/<int:role_id>/",
        DeleteUserRole.as_view(),
        name="Delete User Role",
    ),
    path(
        "get-all-user-roles/<int:page_number>/",
        GetAllUserRoles.as_view(),
        name="Get All User Roles",
    ),
    path(
        "update-user-role/<int:role_id>/",
        UpdateUserRole.as_view(),
        name="Update User Role",
    ),
    path(
        "get-single-role/<int:role_id>/",
        GetSingleRole.as_view(),
        name="Get Single User Role",
    ),
    path(
        "add-module/",
        AddModuleView.as_view(),
        name="Add Module",
    ),
]
