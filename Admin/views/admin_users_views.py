import datetime

from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models import User
from Blog.models.blog_model import BlogPost
from Events.models.events_model import Events
from helpers.email_sender import send_email
from helpers.functions import (aware_datetime, generate_random_string,
                               paginate_data)
from helpers.status_codes import (action_authorization_exception,
                                  cannot_perform_action,
                                  duplicate_data_exception,
                                  non_existing_data_exception)
from helpers.validations import check_required_fields, check_super_admin


# Get system statistics
class GetSystemStatistics(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        if not check_super_admin(self.request.user):
            raise cannot_perform_action("Unauthorized to perform action")

        total_users = User.objects.all().count()
        total_admins = User.objects.filter(is_admin=True).count()
        total_guests = User.objects.filter(account_type="Guest").count()
        total_content_creators = User.objects.filter(
            account_type="Content Creator"
        ).count()

        total_blogs = BlogPost.objects.all().count()
        total_events = Events.objects.all().count()
        total_polls = 0
        total_forums = 0
        total_documents_in_vault = 0
        total_donations = 0

        data = {
            "total_users": total_users,
            "total_admins": total_admins,
            "total_guests": total_guests,
            "total_content_creators": total_content_creators,
            "total_blogs_and_polls": total_blogs + total_polls,
            "total_events_and_forums": total_events + total_forums,
            "total_donations": total_donations,
            "total_documents_in_vault": total_documents_in_vault,
        }

        return JsonResponse(
            {
                "status": "success",
                "detail": "System statistics retrieved successfully",
                "data": data,
            },
            safe=False,
        )


# Get all content creators
class GetAllUsers(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        page_number = self.kwargs.get("page_number")
        account_type = request.data.get("account_type")

        if not check_super_admin(user):
            raise action_authorization_exception("Unauthorized to perform action")
        if account_type == "All":
            users = (
                User.objects.all()
                .values(
                    "user_key",
                    "role_id",
                    "role__name",
                    "email",
                    "first_name",
                    "last_name",
                    "account_type",
                    "organization",
                    "country__name",
                    "is_verified",
                )
                .order_by("-created_on")
            )
        else:
            users = (
                User.objects.filter(account_type=account_type)
                .values(
                    "user_key",
                    "role_id",
                    "role__name",
                    "email",
                    "first_name",
                    "last_name",
                    "organization",
                    "country__name",
                    "is_verified",
                )
                .order_by("-created_on")
            )

        data = paginate_data(users, page_number, 10)

        return JsonResponse(data, safe=False)


# Add Super Admins
class AddSuperAdmins(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data

        if not check_super_admin(user):
            raise action_authorization_exception("Unauthorized to perform action")

        check_required_fields(
            data,
            [
                "email",
                "first_name",
                "last_name",
                "organization",
                "country_id",
                "role_id",
            ],
        )

        try:
            User.objects.get(email=data["email"])
            raise duplicate_data_exception("Email")
        except User.DoesNotExist:
            password = generate_random_string(8)
            data["password"] = make_password(password)
            data["is_verified"] = True
            data["is_admin"] = True
            data["account_type"] = "Super Admin"

            new_user = User.objects.create(**data)

            new_line = "\n"
            double_new_line = "\n\n"
            message = (
                f"Hi, {new_user.first_name}.{new_line}"
                f"You have been added as an Admin on Sema."
                f"Please use the password below to login into your account {new_line}"
                f"Password: {password}{new_line}"
                f"Change your password after logging in. {new_line}"
                f"{double_new_line}The Sema Team"
            )

            send_email(new_user.email, "New Account - Sema", message)

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Admin registered successfully",
                },
                safe=False,
            )


# Delete a user from the database
class DeleteUserView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        data = request.data

        if not check_super_admin(self.request.user):
            raise action_authorization_exception("Unauthorized to perform action")

        check_required_fields(data, ["user_key"])

        try:
            user = User.objects.get(user_key=data["user_key"])
            user.delete()
            return JsonResponse(
                {
                    "status": "success",
                    "detail": "User deleted successfully",
                },
                safe=False,
            )
        except User.DoesNotExist:
            raise non_existing_data_exception("User")


# Get Single User
class GetSingleUser(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        data = request.data

        if not check_super_admin(self.request.user):
            raise action_authorization_exception("Unauthorized to perform action")

        check_required_fields(data, ["user_key"])

        user = (
            User.objects.filter(user_key=data["user_key"])
            .values(
                "user_key",
                "role_id",
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

        if not user:
            raise non_existing_data_exception("User")

        return JsonResponse(
            {
                "status": "success",
                "detail": "User retrieved successfully",
                "data": user,
            },
            safe=False,
        )


# Verify Users
class VerifyUsers(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        data = request.data

        if not check_super_admin(self.request.user):
            raise action_authorization_exception("Unauthorized to perform action")

        check_required_fields(data, ["user_key"])

        try:
            user = User.objects.get(user_key=data["user_key"])
            user.is_verified = True
            user.updated_on = aware_datetime(datetime.datetime.now())
            user.save()

            return JsonResponse(
                {"status": "success", "detail": "User verified successfully"},
                safe=False,
            )
        except User.DoesNotExist:
            raise non_existing_data_exception("User")
