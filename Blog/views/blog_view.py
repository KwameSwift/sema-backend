import json
import os

from django.db.models import Q
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Blog.models.blog_model import BlogComment, BlogPost
from helpers.functions import (check_abusive_words, delete_local_file,
                               local_file_upload, paginate_data)
from helpers.status_codes import (action_authorization_exception,
                                  duplicate_data_exception,
                                  non_existing_data_exception)
from helpers.validations import (check_permission, check_required_fields,
                                 check_super_admin)
from Utilities.models.documents_model import BlogDocuments, UserDocuments

LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")


# Create a new blog post
class CreateBlogPost(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data
        user = self.request.user
        files = request.FILES.getlist("files")
        
        files = data.pop("files", None)
        if not check_permission(user, "Blog", [2]):
            raise action_authorization_exception("Unauthorized to create blog post")

        check_required_fields(data, ["title", "content"])
        abusive_words_check = check_abusive_words(content=data["content"])
        data["censored_content"] = abusive_words_check[0]
        data["is_abusive"] = abusive_words_check[1]
        
        data = json.dumps(data)
        data = json.loads(data)
        
        try:
            BlogPost.objects.get(title=data["title"])
            raise duplicate_data_exception("Blog title")
        except BlogPost.DoesNotExist:
            data["author_id"] = user.user_key
            
            blog = BlogPost.objects.create(**data)

            for file in files:
                full_directory = f"{LOCAL_FILE_PATH}{user.first_name}_{user.last_name}/Blog_Documents/{blog.title}"
                file_path = local_file_upload(full_directory, file)

                new_blog_image = {
                    "owner_id": user.user_key,
                    "blog_id": blog.id,
                    "document_location": file_path,
                }

                BlogDocuments.objects.create(**new_blog_image)

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
                    "total_likes",
                    "total_shares",
                    "censored_content",
                    "is_abusive",
                    "is_approved",
                    "is_published",
                    "reference",
                    "author_id",
                    "author__first_name",
                    "author__last_name",
                    "author__is_verified",
                    "created_on",
                )
                .first()
            )
            blog_comments = BlogComment.objects.filter(blog_id=blog_post["id"]).values(
                "commentor__first_name", "commentor__last_name", "comment"
            )
            blog_post["total_comments"] = blog_comments.count()
            blog_post["comments"] = list(blog_comments)
            blog_post["documents"] = list(
                BlogDocuments.objects.filter(blog_id=blog_post["id"]).values(
                    "id", "document_location"
                )
            )
            blog_post["author_profile_image"] = list(
                UserDocuments.objects.filter(
                    owner=blog_post["author_id"], document_type="Profile Image"
                ).values("id", "document_location")
            )

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
                "total_likes",
                "total_shares",
                "censored_content",
                "is_abusive",
                "is_approved",
                "is_published",
                "reference",
                "author_id",
                "author__first_name",
                "author__last_name",
                "author__is_verified",
                "created_on",
            )
            .order_by("-created_on")
        )

        for blog_post in blog_posts:
            total_comments = BlogComment.objects.filter(blog_id=blog_post["id"]).count()
            blog_post["total_comments"] = total_comments
            blog_post["documents"] = list(
                BlogDocuments.objects.filter(blog_id=blog_post["id"]).values()
            )
            blog_post["author_profile_image"] = list(
                UserDocuments.objects.filter(
                    owner=blog_post["author_id"], document_type="Profile Image"
                ).values("id", "document_location")
            )

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
                "is_approved",
                "total_likes",
                "total_shares",
                "is_published",
                "censored_content",
                "is_abusive",
                "reference",
                "author_id",
                "author__first_name",
                "author__is_verified",
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
            blog_post["documents"] = list(
                BlogDocuments.objects.filter(blog_id=blog_post["id"])
                .values()
                .order_by("-created_on")
            )
            blog_post["author_profile_image"] = (
                UserDocuments.objects.filter(
                    owner=blog_post["author_id"], document_type="Profile Image"
                )
                .values("id", "document_location")
                .first()
            )

        data = paginate_data(blog_posts, page_number, 10)
        return JsonResponse(
            data,
            safe=False,
        )


# Upload blog image
class UploadBlogDocument(APIView):
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
        except BlogPost.DoesNotExist:
            raise non_existing_data_exception("Blog")

        for file in files:
            full_directory = f"{LOCAL_FILE_PATH}{user.first_name}_{user.last_name}/Blog_Images/{blog.title}"
            file_path = local_file_upload(full_directory, file)

            new_blog_image = {
                "owner": user,
                "blog_id": blog.id,
                "document_location": file_path,
            }

            BlogDocuments.objects.create(**new_blog_image)

        return JsonResponse(
            {"status": "success", "detail": "File uploaded successfully"},
            safe=False,
        )


# Delete Blog Image
class DeleteBlogDocuments(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data

        if not check_permission(user, "Blog", [2]):
            raise action_authorization_exception("Unauthorized to delete blog image")

        check_required_fields(data, ["blog_post_id"], ["document_urls"])
        try:
            blog = BlogPost.objects.get(id=data["blog_post_id"])
        except BlogPost.DoesNotExist:
            raise non_existing_data_exception("Blog")

        for url in data["document_urls"]:
            if os.path.exists(url):
                os.remove(url)
            BlogDocuments.objects.filter(blog=blog, document_location=url).delete()

        return JsonResponse(
            {"status": "success", "detail": "File(s) deleted successfully"},
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
            if "content" in data:
                abusive_words_check = check_abusive_words(content=data["content"])
                data["censored_content"] = abusive_words_check[0]
                data["is_abusive"] = abusive_words_check[1]
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

            docs = BlogDocuments.objects.filter(blog_id=blog.id).values(
                "document_location"
            )

            for doc in docs:
                delete_local_file(doc["document_location"])

            BlogDocuments.objects.filter(blog_id=blog.id).delete()

            blog.delete()

            return JsonResponse(
                {"status": "success", "detail": "Blog deleted successfully"},
                safe=False,
            )

        except BlogPost.DoesNotExist:
            raise non_existing_data_exception("Blog")


# Like a Blog
class LikeABlogPost(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        blog_id = self.kwargs["blog_id"]

        try:
            blog = BlogPost.objects.get(id=blog_id)
            exists = BlogPost.likers.through.objects.filter(
                Q(blogpost_id=blog_id) & Q(user_id=user.user_key)
            )
            if exists:
                likes = blog.total_likes - 1
                blog.likers.remove(user)
                message = "Blog unliked"
            else:
                blog.likers.add(user)
                likes = blog.total_likes + 1
                message = "Blog liked"

            blog.total_likes = likes
            blog.save()

            return JsonResponse(
                {"status": "success", "detail": message, "total_likes": likes},
                safe=False,
            )
        except BlogPost.DoesNotExist:
            raise non_existing_data_exception("Blog")


# Share a Blog
class ShareABlogPost(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        blog_id = self.kwargs["blog_id"]

        try:
            blog = BlogPost.objects.get(id=blog_id)

            shares = blog.total_shares + 1
            blog.total_shares = shares
            blog.save()

            return JsonResponse(
                {"status": "success", "detail": "Blog shared", "total_shares": shares},
                safe=False,
            )
        except BlogPost.DoesNotExist:
            raise non_existing_data_exception("Blog")
