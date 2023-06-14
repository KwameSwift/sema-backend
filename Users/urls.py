from django.urls import path

from .views.users_views import (DeleteProfileImage, GetAuthorStatistics,
                                GetUserBlogPosts, ProfileView,
                                UploadProfileImage, UploadUserDocuments)

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
        "my-blog-posts/<int:page_number>/",
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
        "upload-profile-image/",
        UploadProfileImage.as_view(),
        name="Upload Profile Image",
    ),
]
