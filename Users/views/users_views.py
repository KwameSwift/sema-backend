import json
import os

from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models.user_model import User
from Blog.models.blog_model import BlogComment, BlogPost
from Events.models.events_model import Events
from helpers.functions import (convert_quill_text_to_normal_text, delete_file,
                               local_file_upload, paginate_data, truncate_text)
from helpers.status_codes import (action_authorization_exception,
                                  cannot_perform_action,
                                  non_existing_data_exception)
from helpers.validations import check_required_fields
from helpers.azure_file_handling import delete_blob, upload_profile_image
from Polls.models.poll_models import Poll
from Polls.poll_helper import retrieve_poll_with_choices
from Utilities.models.documents_model import UserDocuments

LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")


# View my profile
class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        usr = self.request.user
        user = (
            User.objects.filter(user_key=usr.user_key)
            .values(
                "user_key",
                "role__name",
                "email",
                "first_name",
                "last_name",
                "profile_image",
                "bio",
                "links",
                "organization",
                "mobile_number",
                "account_type",
                "country__calling_code",
                "country__flag",
                "country__name",
                "is_verified",
            )
            .first()
        )

        return JsonResponse(
            {
                "status": "success",
                "detail": "Profile retrieved successfully",
                "data": user,
            },
            safe=False,
        )


# Upload user documents
class UploadUserDocuments(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist("files")
        user = self.request.user

        LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")
        for file in files:
            full_directory = (
                f"{LOCAL_FILE_PATH}{user.first_name}_{user.last_name}/Documents"
            )
            file_path = local_file_upload(full_directory, file)

            new_event_image = {
                "owner": user,
                "document_type": "Personal Documents",
                "document_location": file_path,
            }

            UserDocuments.objects.create(**new_event_image)

        return JsonResponse(
            {"status": "success", "detail": "Documents uploaded successfully"},
            safe=False,
        )


# Get all blog posts created by a user
class GetUserBlogPosts(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        page_number = self.kwargs.get("page_number")
        data_type = self.kwargs.get("data_type")

        if user.account_type == "Guest":
            raise action_authorization_exception("Unauthorized to view Blogs")

        query = Q(author=user)
        if data_type == 1:
            query &= Q(is_approved=True)
        elif data_type == 2:
            query &= Q(is_approved=False)

        blog_posts = (
            BlogPost.objects.filter(query)
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
                "is_approved",
                "is_published",
                "approved_and_published_by__first_name",
                "approved_and_published_by__last_name",
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
            converted_text = convert_quill_text_to_normal_text(blog_post["content"])
            blog_post["preview_text"] = truncate_text(converted_text, 200)
            total_comments = BlogComment.objects.filter(
                blog_id=blog_post["id"]
            ).values()
            blog_post["total_comments"] = total_comments.count()

        data = paginate_data(blog_posts, page_number, 10)
        return JsonResponse(
            data,
            safe=False,
        )


# Delete Profile Image
class DeleteProfileImage(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        user = self.request.user

        if user.profile_image:
            delete_file(user.profile_image)
            user.profile_image = None
            user.save()
        else:
            raise cannot_perform_action("No image to delete")

        return JsonResponse(
            {"status": "success", "detail": "Profile image deleted successfully"},
            safe=False,
        )


# Get my statistics
class GetAuthorStatistics(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user

        total_blogs = BlogPost.objects.filter(author=user).count()
        total_events = Events.objects.filter(created_by=user).count()
        total_polls = Poll.objects.filter(author=user).count()
        total_forums = 0

        blogs = (
            BlogPost.objects.filter(author=user)
            .annotate(month=TruncMonth("created_on"))
            .values("month")
            .annotate(count=Count("id"))
        )
        blog_data = [
            {"month": entry["month"].strftime("%m-%Y"), "count": entry["count"]}
            for entry in blogs
        ]

        data = {
            "total_polls": total_polls,
            "total_blogs": total_blogs,
            "total_events": total_events,
            "total_forums": total_forums,
            "blog_data": blog_data,
        }

        return JsonResponse(
            {
                "status": "success",
                "detail": "Statistics retrieved successfully",
                "data": data,
            },
            safe=False,
        )


# Search blogs
class SearchMyBlogPosts(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        page_number = self.kwargs.get("page_number")
        data = request.data

        check_required_fields(data, ["search_query"])

        blog_posts = (
            BlogPost.objects.filter(
                Q(title__icontains=data["search_query"], author=user)
                | Q(description__icontains=data["search_query"], author=user)
                | Q(author__first_name__icontains=data["search_query"], author=user)
                | Q(author__last_name__icontains=data["search_query"], author=user)
            )
            .values(
                "id",
                "title",
                "content",
                "description",
                "is_approved",
                "total_likes",
                "total_shares",
                "is_published",
                "approved_and_published_by__first_name",
                "approved_and_published_by__last_name",
                "cover_image",
                "links",
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
            total_comments = (
                BlogComment.objects.filter(blog_id=blog_post["id"])
                .values()
                .order_by("-created_on")
            )
            blog_post["total_comments"] = total_comments.count()

        data = paginate_data(blog_posts, page_number, 10)
        return JsonResponse(
            data,
            safe=False,
        )


# Update User Profile
class UpdateUserProfile(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data
        profile_image = request.FILES.get("profile_image")

        user = User.objects.get(user_key=user.user_key)
        container = f"{user.first_name}-{user.last_name}"

        if profile_image:
            try:
                user_doc = UserDocuments.objects.get(owner=user, document_type="Profile Image")
                delete_blob(container, user_doc.document_key)
                user_doc.delete()
            except UserDocuments.DoesNotExist:
                pass
            image = upload_profile_image(profile_image, user) 
            user.profile_image = image
            profile_image = data.pop("profile_image", None)
            user.save()

        data = json.dumps(data)
        data = json.loads(data)

        User.objects.filter(user_key=user.user_key).update(**data)

        return JsonResponse(
            {"status": "success", "detail": "User profile updated successfully"},
            safe=False,
        )


class GetMySinglePoll(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        poll_id = self.kwargs.get("poll_id")

        try:
            poll = Poll.objects.get(id=poll_id, author=user)
            poll_data = retrieve_poll_with_choices(poll.id)

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Poll retrieved successfully",
                    "data": poll_data,
                },
                safe=False,
            )
        except Poll.DoesNotExist:
            raise non_existing_data_exception("Poll")
