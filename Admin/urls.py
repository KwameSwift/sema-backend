from django.urls import path

from DocumentVault.views.document_vault_views import AdminGetAllDocumentsInVault
from .views.admin_blog_views import (
    ApproveAndPublishBlogs,
    GetAllBlogPostsAsAdmin,
    DeclineBlogs,
)
from .views.admin_events_view import ApproveEvents, GetAllEventsAsAdmin
from .views.admin_forum_views import ApproveForum, DeclineForum, AdminGetAllForums
from .views.admin_poll_views import (
    AdminGetAllPolls,
    AdminViewSinglePoll,
    ApprovePoll,
    DeclinePoll,
)
from .views.admin_user_roles_views import (
    AddModuleView,
    AddUserRole,
    AssignUserRoleToUser,
    DeleteUserRole,
    GetAllUserRoles,
    GetSingleRole,
    UpdateUserRole,
)
from .views.admin_users_views import (
    AddSuperAdmins,
    DeleteUserView,
    GetAllUsers,
    GetSingleUser,
    GetSystemStatistics,
    SearchAllUsers,
    VerifyUsers,
)

urlpatterns = [
    # System Statistics
    path(
        "system-statistics/",
        GetSystemStatistics.as_view(),
        name="Get System Statistics",
    ),
    # Blog
    path(
        "all-blog-posts/<int:data_type>/<int:page_number>/",
        GetAllBlogPostsAsAdmin.as_view(),
        name="Admin All Blog Posts",
    ),
    path(
        "approve-blog-posts/",
        ApproveAndPublishBlogs.as_view(),
        name="Admin Approve Blog Post",
    ),
    path(
        "decline-blog-posts/",
        DeclineBlogs.as_view(),
        name="Admin Decline Blog Post",
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
        "get-single-user/<slug:user_key>/",
        GetSingleUser.as_view(),
        name="Get Single User",
    ),
    path(
        "delete-single-user/<slug:user_key>/",
        DeleteUserView.as_view(),
        name="Delete Single User",
    ),
    path(
        "add-users/",
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
    path(
        "search-users/<int:page_number>/",
        SearchAllUsers.as_view(),
        name="Search All Users",
    ),
    # Polls
    path(
        "approve-poll/<int:poll_id>/",
        ApprovePoll.as_view(),
        name="Approve Poll",
    ),
    path(
        "decline-poll/<int:poll_id>/",
        DeclinePoll.as_view(),
        name="Decline Poll",
    ),
    path(
        "single-poll/<int:poll_id>/",
        AdminViewSinglePoll.as_view(),
        name="Admin Single Poll",
    ),
    path(
        "get-all-polls/<int:data_type>/<int:page_number>/",
        AdminGetAllPolls.as_view(),
        name="Admin Get All Polls",
    ),
    # Forum
    path(
        "approve-disapprove-forum/<int:status>/<int:forum_id>/",
        ApproveForum.as_view(),
        name="Approve Or Disapprove Forum",
    ),
    path(
        "decline-forum/<int:forum_id>/",
        DeclineForum.as_view(),
        name="Decline Forum",
    ),
    path(
        "get-all-forums/<int:data_type>/<int:page_number>/",
        AdminGetAllForums.as_view(),
        name="Admin Get All Forums",
    ),
    path(
        "get-vault-documents/<int:page_number>/",
        AdminGetAllDocumentsInVault.as_view(),
        name="Admin Get All Documents In Vault",
    ),
]
