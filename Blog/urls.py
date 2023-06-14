from django.urls import path

from .views.blog_view import (CommentOnBlogPost, CreateBlogPost,
                              DeleteBlogDocuments, DeleteBlogPost,
                              GetAllPublishedBlogPost, GetSingleBlogPost,
                              LikeABlogPost, UpdateBlogPost,
                              UploadBlogDocument)

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
        "upload-blog-documents/",
        UploadBlogDocument.as_view(),
        name="Upload Blog Document",
    ),
    path(
        "delete-blog-documents/",
        DeleteBlogDocuments.as_view(),
        name="Delete Blog Image",
    ),
    path(
        "update-blog-post/",
        UpdateBlogPost.as_view(),
        name="Update Blog Post",
    ),
    path(
        "delete-blog-post/",
        DeleteBlogPost.as_view(),
        name="Delete Blog Post",
    ),
    path(
        "like-blog-post/<int:blog_id>/",
        LikeABlogPost.as_view(),
        name="Like A Blog Post",
    ),
]
