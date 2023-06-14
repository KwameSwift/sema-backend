import os

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Blog.models.blog_model import BlogComment, BlogPost
from helpers.functions import delete_file, paginate_data, upload_files
from helpers.status_codes import (action_authorization_exception,
                                  duplicate_data_exception,
                                  non_existing_data_exception)
from helpers.validations import (check_permission, check_required_fields,
                                 check_super_admin)


# Create a new blog post
class CreateBlogPost(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data
        user = self.request.user

        if not check_permission(user, "Blog", [2]):
            raise action_authorization_exception("Unauthorized to create blog post")

        check_required_fields(data, ["title", "content"])

        try:
            BlogPost.objects.get(title=data["title"])
            raise duplicate_data_exception("Blog title")
        except BlogPost.DoesNotExist:
            data["author"] = user
            blog = BlogPost.objects.create(**data)

            blog_data = BlogPost.objects.filter(id=blog.id).values().first()

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Blog created and submitted for review",
                    "data": blog_data,
                },
                safe=False,
            )


# Comment on Post
class CommentOnBlogPost(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data

        check_required_fields(data, ["comment", "blog_post_id"])

        try:
            blog_post = BlogPost.objects.get(id=data["blog_post_id"])
            BlogComment.objects.create(
                blog_id=blog_post.id, commentor=user, comment=data["comment"]
            )
            return JsonResponse(
                {"status": "success", "detail": "Comment posted"},
                safe=False,
            )
        except BlogPost.DoesNotExist:
            raise non_existing_data_exception("Blog")


# Get Single Blog Post
class GetSingleBlogPost(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        blog_post_id = self.kwargs["blog_post_id"]

        try:
            BlogPost.objects.get(id=blog_post_id)
            blog_post = (
                BlogPost.objects.filter(id=blog_post_id)
                .values(
                    "id",
                    "title",
                    "content",
                    "description",
                    "blog_image_location",
                    "is_approved",
                    "is_published",
                    "blog_links",
                    "author__first_name",
                    "author__last_name",
                    "created_on",
                )
                .first()
            )
            blog_comments = BlogComment.objects.filter(blog_id=blog_post["id"]).values(
                "commentor__first_name", "commentor__last_name", "comment"
            )
            blog_post["total_comments"] = blog_comments.count()
            blog_post["comments"] = list(blog_comments)

            return JsonResponse(
                {"status": "success", "detail": "Comment posted", "data": blog_post},
                safe=False,
            )
        except BlogPost.DoesNotExist:
            raise non_existing_data_exception("Blog")


# Get all blog posts by admin
class GetAllBlogPostsAsAdmin(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        page_number = self.kwargs.get("page_number")

        if not check_super_admin(user):
            raise action_authorization_exception("Unauthorized to view Blog Posts")

        blog_posts = (
            BlogPost.objects.all()
            .values(
                "id",
                "title",
                "content",
                "description",
                "blog_image_location",
                "is_approved",
                "is_published",
                "blog_links",
                "author__first_name",
                "author__last_name",
                "created_on",
            )
            .order_by("-created_on")
        )

        for blog_post in blog_posts:
            total_comments = BlogComment.objects.filter(blog_id=blog_post["id"]).count()
            blog_post["total_comments"] = total_comments

        data = paginate_data(blog_posts, page_number, 10)
        return JsonResponse(
            data,
            safe=False,
        )


# Get all published blog posts
class GetAllPublishedBlogPost(APIView):
    def get(self, request, *args, **kwargs):
        page_number = self.kwargs.get("page_number")

        blog_posts = (
            BlogPost.objects.filter(is_approved=True, is_published=True)
            .values(
                "id",
                "title",
                "content",
                "description",
                "blog_image_location",
                "is_approved",
                "is_published",
                "blog_links",
                "author__first_name",
                "author__last_name",
                "created_on",
            )
            .order_by("-created_on")
        )

        for blog_post in blog_posts:
            comments = (
                BlogComment.objects.filter(blog_id=blog_post["id"])
                .values(
                    "id",
                    "commentor__first_name",
                    "commentor__last_name",
                    "comment",
                    "created_on",
                )
                .order_by("-created_on")
            )
            blog_post["total_comments"] = comments.count()
            blog_post["comments"] = list(comments)

        data = paginate_data(blog_posts, page_number, 10)
        return JsonResponse(
            data,
            safe=False,
        )


# Upload blog image
class UploadBlogImage(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        files = request.FILES.getlist("files")
        data = request.data

        if not check_permission(user, "Blog", [2]):
            raise action_authorization_exception("Unauthorized to upload blog image")

        check_required_fields(data, ["blog_post_id"])
        try:
            blog = BlogPost.objects.get(id=data["blog_post_id"])
            if blog.author != user:
                raise action_authorization_exception(
                    "Unauthorized to upload blog image for this blog"
                )
        except BlogPost.DoesNotExist:
            raise non_existing_data_exception("Blog")

        LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")
        for file in files:
            file_name = str(file.name)
            new_name = file_name.replace(" ", "_")
            fs = FileSystemStorage(location=LOCAL_FILE_PATH)
            fs.save(new_name, file)

            file_path = LOCAL_FILE_PATH + new_name

            subdirectory = (
                f"{user.first_name}_{user.last_name}/Blog_Images/{blog.title}"
            )
            uploaded_path = upload_files(file_path, subdirectory)

            blog.blog_image_location = uploaded_path
            blog.save()
            if os.path.exists(file_path):
                os.remove(file_path)

        return JsonResponse(
            {"status": "success", "detail": "File uploaded successfully"},
            safe=False,
        )


# Delete Blog Image
class DeleteBlogImage(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data

        if not check_permission(user, "Blog", [2]):
            raise action_authorization_exception("Unauthorized to delete blog image")

        check_required_fields(data, ["blog_post_id"])
        try:
            blog = BlogPost.objects.get(id=data["blog_post_id"])
            if blog.author != user:
                raise action_authorization_exception(
                    "Unauthorized to delete blog image for this blog"
                )
        except BlogPost.DoesNotExist:
            raise non_existing_data_exception("Blog")

        delete_file(blog.blog_image_location)

        blog.blog_image_location = None
        blog.save()

        return JsonResponse(
            {"status": "success", "detail": "File deleted successfully"},
            safe=False,
        )


# Update a blog post
class UpdateBlogPost(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        data = request.data
        user = self.request.user

        if not check_permission(user, "Blog", [2]):
            raise action_authorization_exception("Unauthorized to create blog post")

        check_required_fields(data, ["blog_post_id"])

        try:
            BlogPost.objects.get(id=data["blog_post_id"])
            blog_id = data.pop("blog_post_id", None)
            BlogPost.objects.filter(id=blog_id).update(**data)

            blog_data = BlogPost.objects.filter(id=blog_id).values().first()

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Blog updated successfully",
                    "data": blog_data,
                },
                safe=False,
            )

        except BlogPost.DoesNotExist:
            raise non_existing_data_exception("Blog")


# Update a blog post
class DeleteBlogPost(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        data = request.data
        user = self.request.user

        if not check_permission(user, "Blog", [2]):
            raise action_authorization_exception("Unauthorized to create blog post")

        check_required_fields(data, ["blog_post_id"])

        try:
            blog = BlogPost.objects.get(id=data["blog_post_id"])

            delete_file(blog.blog_image_location)

            blog.delete()

            return JsonResponse(
                {"status": "success", "detail": "Blog deleted successfully"},
                safe=False,
            )

        except BlogPost.DoesNotExist:
            raise non_existing_data_exception("Blog")
