from django.urls import path

from .views.users_views import (DeleteProfileImage, GetUserBlogPosts,
                                ProfileView, UploadProfileImage,
                                UploadUserDocuments, GetAuthorStatistics)

urlpatterns = [
    # Users
    path(
        "upload-profile-image/",
        UploadProfileImage.as_view(),
        name="Upload Profile Image",
    ),
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
]
