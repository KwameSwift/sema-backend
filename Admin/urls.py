from django.urls import path

from .views.admin_blog_views import (ApproveAndPublishBlogs,
                                     GetAllBlogPostsAsAdmin)
from .views.admin_events_view import ApproveEvents, GetAllEventsAsAdmin
from .views.admin_user_roles_views import (AddModuleView, AddUserRole,
                                           AssignUserRoleToUser,
                                           DeleteUserRole, GetAllUserRoles,
                                           GetSingleRole, UpdateUserRole)
from .views.admin_users_views import (AddSuperAdmins, DeleteUserView,
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
        "all-blog-posts/<int:data_type>/<int:blog_post_id>/",
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
        "get-all-events/<int:page_number>/",
        GetAllEventsAsAdmin.as_view(),
        name="Admin Get All Events",
    ),
    path(
        "approve-event/",
        ApproveEvents.as_view(),
        name="Admin Approve Events",
    ),
]