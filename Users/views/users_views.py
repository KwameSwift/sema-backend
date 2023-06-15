import os

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models.user_model import User
from Blog.models.blog_model import BlogComment, BlogPost
from Events.models.events_model import Events
from helpers.functions import (check_abusive_words, delete_file,
                               local_file_upload, paginate_data)
from helpers.status_codes import (action_authorization_exception,
                                  cannot_perform_action)
from Utilities.models.documents_model import UserDocuments

LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")


# Upload profile image
class UploadProfileImage(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        file = request.FILES["file"]
        user = self.request.user

        try:
            profile_image = UserDocuments.objects.get(
                owner=user, document_type="Profile Image"
            )
            url = profile_image.document_location
            if os.path.exists(url):
                os.remove(url)
            profile_image.delete()
        except UserDocuments.DoesNotExist:
            pass

        full_directory = (
            f"{LOCAL_FILE_PATH}{user.first_name}_{user.last_name}/Profile_Image"
        )
        file_path = local_file_upload(full_directory, file)

        new_profile_image = {
            "owner": user,
            "document_type": "Profile Image",
            "document_location": file_path,
        }

        UserDocuments.objects.create(**new_profile_image)

        return JsonResponse(
            {
                "status": "success",
                "detail": "File(s) uploaded successfully",
                "profile_image": file_path,
            },
            safe=False,
        )


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

        if user.account_type == "Guest":
            raise action_authorization_exception("Unauthorized to view Blogs")

        blog_posts = (
            BlogPost.objects.filter(author=user)
            .values(
                "id",
                "title",
                "content",
                "description",
                "total_likes",
                "total_shares",
                "is_approved",
                "is_published",
                "reference",
                "author__first_name",
                "author__last_name",
                "author__is_verified",
                "created_on",
            )
            .order_by("-created_on")
        )

        for blog_post in blog_posts:
            total_comments = (
                BlogComment.objects.filter(blog_id=blog_post["id"])
                .values("id", "comment", "commentor__first_name", "commentor_last_name")
                .order_by("-created_on")
            )
            blog_post["total_comments"] = total_comments.count()
            blog_post["comments"] = total_comments

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
        total_polls = 0
        total_donations = 0
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
            "total_blogs_and_polls": total_blogs + total_polls,
            "total_events": total_events,
            "total_donations": total_donations,
            "total_forums": total_forums,
            "blog_data": blog_data
        }

        return JsonResponse(
            {
                "status": "success",
                "detail": "Statistics retrieved successfully",
                "data": data,
            },
            safe=False,
        )
