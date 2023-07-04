from django.urls import path

from .views.users_views import (DeleteProfileImage, GetAuthorStatistics,
                                GetUserBlogPosts, ProfileView,
                                SearchMyBlogPosts, UpdateUserProfile,
                                UploadUserDocuments)
from Polls.views.polls_view import GetAllApprovedPollsByUser, GetMyPolls

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
        "my-polls/<int:data_type>/",
        GetMyPolls.as_view(),
        name="Get My Polls",
    ),
]
