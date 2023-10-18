import datetime

from django.db.models import Q
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models import User
from Blog.blog_helper import send_blog_declination_mail
from Blog.models.blog_model import BlogComment, BlogPost
from helpers.functions import (aware_datetime,
                               convert_quill_text_to_normal_text,
                               paginate_data, truncate_text)
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

        blog_posts = (
            BlogPost.objects.filter(
                Q(is_approved=True)
                if data_type == 1
                else Q(is_approved=False)
                if data_type == 2
                else Q()
            )
            .values(
                "id",
                "title",
                "content",
                "description",
                "total_likes",
                "total_shares",
                "cover_image",
                "censored_content",
                "is_abusive",
                "links",
                "is_approved",
                "is_published",
                "reference",
                "author_id",
                "approved_and_published_by__first_name",
                "approved_and_published_by__last_name",
                "author__first_name",
                "author__last_name",
                "author__is_verified",
                "created_on",
            )
            .order_by("-created_on")
        )

        for blog_post in blog_posts:
            converted_text = convert_quill_text_to_normal_text(blog_post["content"])
            blog_post["preview_text"] = truncate_text(converted_text, 200)
            total_comments = (
                BlogComment.objects.filter(blog_id=blog_post["id"])
                .values(
                    "id",
                    "comment",
                    "commentor__first_name",
                    "commentor__last_name",
                    "created_on",
                )
                .order_by("-created_on")
            )
            blog_post["total_comments"] = total_comments.count()
            blog_post["comments"] = list(total_comments)

        data = paginate_data(blog_posts, page_number, 10)
        return JsonResponse(
            data,
            safe=False,
        )


class DeclineBlogs(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data

        if not check_super_admin(self.request.user):
            raise action_authorization_exception("Unauthorized to perform action")

        check_required_fields(data, ["blog_post_id", "comments"])

        try:
            blog = BlogPost.objects.get(id=data["blog_post_id"])
            blog.is_approved = False
            blog.is_published = False
            blog.is_declined = True
            blog.declined_by = user
            blog.approved_and_published_by = None
            blog.updated_on = aware_datetime(datetime.datetime.now())
            blog.save()

            send_blog_declination_mail(blog, data["comments"])

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Blog verified and published successfully",
                },
                safe=False,
            )
        except User.DoesNotExist:
            raise non_existing_data_exception("User")
