from django.urls import path

from Polls.views.polls_view import GetAllApprovedPollsByUser, GetMyPolls

from .views.users_views import (
    DeleteProfileImage,
    GetAuthorStatistics,
    GetMySinglePoll,
    GetUserBlogPosts,
    ProfileView,
    SearchMyBlogPosts,
    UpdateUserProfile,
    UploadUserDocuments,
    GetMyForums,
    ApproveJoinForumRequest,
    DeclineJoinForumRequest,
    GetForumJoinRequests,
    ManageMyForum,
)

urlpatterns = [
    # Users
    path(
        "upload-user-documents/",
        UploadUserDocuments.as_view(),
        name="Upload User Documents",
    ),
    path(
        "my-profile/",
        ProfileView.as_view(),
        name="Profile View",
    ),
    path(
        "my-blog-posts/<int:data_type>/<int:page_number>/",
        GetUserBlogPosts.as_view(),
        name="User BlogPosts",
    ),
    path(
        "delete-profile-image/",
        DeleteProfileImage.as_view(),
        name="Delete Profile Image",
    ),
    path(
        "my-statistics/",
        GetAuthorStatistics.as_view(),
        name="Get My Statistics",
    ),
    path(
        "search-my-blogs/",
        SearchMyBlogPosts.as_view(),
        name="Search My Blog Posts",
    ),
    path(
        "update-my-profile/",
        UpdateUserProfile.as_view(),
        name="Update My Profile",
    ),
    path(
        "approved-polls/",
        GetAllApprovedPollsByUser.as_view(),
        name="Authenticated User Approved Polls",
    ),
    path(
        "my-polls/<int:data_type>/<int:page_number>/",
        GetMyPolls.as_view(),
        name="Get My Polls",
    ),
    path(
        "my-single-polls/<int:poll_id>/",
        GetMySinglePoll.as_view(),
        name="Get My Single Poll",
    ),
    path(
        "my-forums/<int:data_type>/<int:page_number>/",
        GetMyForums.as_view(),
        name="Get My Forums",
    ),
    path(
        "approve-forum-request/<int:request_id>/",
        ApproveJoinForumRequest.as_view(),
        name="Approve Forum Request",
    ),
    path(
        "decline-forum-request/<int:request_id>/",
        DeclineJoinForumRequest.as_view(),
        name="Decline Forum Request",
    ),
    path(
        "get-forum-join-requests/<int:forum_id>/<int:page_number>/",
        GetForumJoinRequests.as_view(),
        name="Get Forum Join Requests",
    ),
    path(
        "manage-forum/<int:forum_id>/",
        ManageMyForum.as_view(),
        name="Manage My Forum",
    ),
]
