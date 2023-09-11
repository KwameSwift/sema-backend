from django.urls import path

from .views.forum_views import (
    GetSingleForum,
    CreateForum,
    DeleteForum,
    GetAllForums,
    LikeAForum,
    JoinForum,
    LeaveForum,
    UpdateForum,
    SearchForum,
    UploadForumFiles,
)

urlpatterns = [
    # Forums
    path(
        "create-forum/",
        CreateForum.as_view(),
        name="Create Forum",
    ),
    path(
        "get-forum/<int:forum_id>/",
        GetSingleForum.as_view(),
        name="Get Single Forum",
    ),
    path(
        "delete-forum/<int:forum_id>/",
        DeleteForum.as_view(),
        name="Delete Forum",
    ),
    path(
        "get-all-forums/<int:page_number>/",
        GetAllForums.as_view(),
        name="Get All Forums",
    ),
    path(
        "like-a-forum/<int:forum_id>/",
        LikeAForum.as_view(),
        name="Like A Forum",
    ),
    path(
        "join-forum/<int:forum_id>/",
        JoinForum.as_view(),
        name="Join Forum",
    ),
    path(
        "leave-forum/<int:forum_id>/",
        LeaveForum.as_view(),
        name="Leave Forum",
    ),
    path(
        "update-forum/<int:forum_id>/",
        UpdateForum.as_view(),
        name="Update Forum",
    ),
    path(
        "search-forums/<int:page_number>/",
        SearchForum.as_view(),
        name="Search Forums",
    ),
    path(
        "upload-forum-files/<int:forum_id>/",
        UploadForumFiles.as_view(),
        name="Upload Forum Files",
    ),
]
