import os

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models.user_model import User
from Blog.models.blog_model import BlogComment, BlogPost
from Events.models.events_model import Events
from helpers.functions import (delete_file, local_file_upload, paginate_data,
                               upload_files)
from helpers.status_codes import (action_authorization_exception,
                                  cannot_perform_action,
                                  non_existing_data_exception)
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
            file_name = str(file.name)
            new_name = file_name.replace(" ", "_")
            fs = FileSystemStorage(location=LOCAL_FILE_PATH)
            fs.save(new_name, file)

            file_path = LOCAL_FILE_PATH + new_name

            subdirectory = f"{user.first_name}_{user.last_name}/Documents"
            uploaded_path = upload_files(file_path, subdirectory)

            user_documents = {"user": user, "document_location": uploaded_path}

            if os.path.exists(file_path):
                os.remove(file_path)

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
                "blog_links",
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

        data = {
            "total_blogs": total_blogs,
            "total_events": total_events,
            "total_polls": 0,
            "total_donations": 0,
            "total_forums": 0,
            "total_documents_in_vault": 0,
        }

        return JsonResponse(
            {
                "status": "success",
                "detail": "Statistics retrieved successfully",
                "data": data,
            },
            safe=False,
        )
