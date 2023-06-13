import datetime
import os

from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models import User
from Blog.models.blog_model import BlogComment, BlogPost
from helpers.functions import aware_datetime, paginate_data
from helpers.status_codes import (action_authorization_exception,
                                  non_existing_data_exception)
from helpers.validations import check_required_fields, check_super_admin


# Approve and Publish Blogs
class ApproveAndPublishBlogs(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data

        if not check_super_admin(self.request.user):
            raise action_authorization_exception("Unauthorized to perform action")

        check_required_fields(data, ["blog_post_id"])

        try:
            blog = BlogPost.objects.get(id=data["blog_post_id"])
            blog.is_approved = True
            blog.is_published = True
            blog.approved_and_published_by = user
            blog.updated_on = aware_datetime(datetime.datetime.now())
            blog.save()

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Blog verified and published successfully",
                },
                safe=False,
            )
        except User.DoesNotExist:
            raise non_existing_data_exception("User")


# Get all blog posts by admin
class GetAllBlogPostsAsAdmin(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        page_number = self.kwargs.get("page_number")
        data_type = self.kwargs.get("data_type")

        if not check_super_admin(user):
            raise action_authorization_exception("Unauthorized to view Blog Posts")
        if data_type == 1:
            is_approved = True
        else:
            is_approved = False
        blog_posts = (
            BlogPost.objects.filter(is_approved=is_approved)
            .values(
                "id",
                "title",
                "content",
                "author__first_name",
                "author__last_name",
                "blog_links",
                "blog_image_location",
                "is_approved",
                "is_published",
                "created_on",
            )
            .order_by("-created_on")
        )

        for blog_post in blog_posts:
            total_comments = BlogComment.objects.filter(blog_id=blog_post["id"]).count()
            blog_post["total_comments"] = total_comments

        data = paginate_data(blog_posts, page_number, 3)
        return JsonResponse(
            data,
            safe=False,
        )
