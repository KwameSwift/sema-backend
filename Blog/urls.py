from django.urls import path

from .views.blog_view import (CommentOnBlogPost, CreateBlogPost,
                              DeleteBlogImage, GetAllPublishedBlogPost,
                              GetSingleBlogPost, UploadBlogImage)

urlpatterns = [
    # Blog
    path("create-blog/", CreateBlogPost.as_view(), name="Create Blog"),
    path(
        "comment-on-blog-post/",
        CommentOnBlogPost.as_view(),
        name="Comment On BlogPosts",
    ),
    path(
        "single-blog-post/<int:blog_post_id>/",
        GetSingleBlogPost.as_view(),
        name="Single BlogPost",
    ),
    path(
        "all-published-blogs/<int:page_number>/",
        GetAllPublishedBlogPost.as_view(),
        name="All Published BlogPost",
    ),
    path(
        "upload-blog-image/",
        UploadBlogImage.as_view(),
        name="Upload Blog Image",
    ),
    path(
        "delete-blog-image/",
        DeleteBlogImage.as_view(),
        name="Delete Blog Image",
    ),
]
