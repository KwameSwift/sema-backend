from django.urls import path

from .views.admin_user_roles_views import (AddModuleView, AddUserRole,
                                           DeleteUserRole, GetAllUserRoles,
                                           GetSingleRole, UpdateUserRole)
from .views.admin_views import (AddSuperAdmins, ApproveAndPublishBlogs,
                                AssignUserRoleToUser, DeleteUserView,
                                GetAllBlogPostsAsAdmin, GetAllEventsAsAdmin,
                                GetAllUsers, GetSingleUser,
                                GetSystemStatistics, VerifyUsers)

urlpatterns = [
    # System Statistics
    path(
        "system-statistics/",
        GetSystemStatistics.as_view(),
        name="Get System Statistics",
    ),
    # Blog
    path(
        "all-blog-posts/<int:blog_post_id>/",
        GetAllBlogPostsAsAdmin.as_view(),
        name="Admin All Blog Posts",
    ),
    path(
        "approve-blog-posts/",
        ApproveAndPublishBlogs.as_view(),
        name="Admin Approve Blog Post",
    ),
    # Users
    path(
        "all-users/<int:page_number>/",
        GetAllUsers.as_view(),
        name="All Users",
    ),
    path(
        "verify-users/",
        VerifyUsers.as_view(),
        name="Verify Users",
    ),
    path(
        "get-single-user/",
        GetSingleUser.as_view(),
        name="Get Single User",
    ),
    path(
        "delete-single-user/",
        DeleteUserView.as_view(),
        name="Delete Single User",
    ),
    path(
        "add-admins/",
        AddSuperAdmins.as_view(),
        name="Add Admins",
    ),
    path("assign-user-role/", AssignUserRoleToUser.as_view(), name="Assign User Role"),
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
    # Modules
    path(
        "add-module/",
        AddModuleView.as_view(),
        name="Add Module",
    ),
    # Events
    path(
        "get-all-events/",
        GetAllEventsAsAdmin.as_view(),
        name="Admin Get All Events",
    ),
]
