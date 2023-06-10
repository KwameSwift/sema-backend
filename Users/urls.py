from django.urls import path

from .views.users_views import (AddSuperAdmins, AssignUserRoleToUser,
                                DeleteUserView, GetAllUsers, GetSingleUser)
from .views.utilities_view import DropDowns

urlpatterns = [
    # Dropdowns
    path(
        "dropdowns/<int:drop_type>/",
        DropDowns.as_view(),
        name="All Dropdowns",
    ),
    
    # Users
    path(
        "all-users/<int:page_number>/",
        GetAllUsers.as_view(),
        name="All Users",
    ),
    path(
        "add-admins/",
        AddSuperAdmins.as_view(),
        name="Add Admins",
    ),
    path(
        "assign-user-roles/",
        AssignUserRoleToUser.as_view(),
        name="Assign User Roles",
    ),
    path(
        "delete-user/",
        DeleteUserView.as_view(),
        name="Delete User",
    ),
    path(
        "get-user/",
        GetSingleUser.as_view(),
        name="Get User",
    ),
]
