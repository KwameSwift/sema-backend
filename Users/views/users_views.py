import datetime

from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.utils.timezone import make_aware
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models.user_model import User, UserRole
from helpers.email_sender import send_email
from helpers.functions import generate_random_string, paginate_data
from helpers.status_codes import (action_authorization_exception,
                                  duplicate_data_exception,
                                  non_existing_data_exception)
from helpers.validations import check_required_fields, check_super_admin


# Get all content creators
class GetAllUsers(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        page_number = self.kwargs.get("page_number")
        account_type = request.data.get("account_type")

        if not check_super_admin(user):
            raise action_authorization_exception("Unauthorized to perform action")

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
            ["email", "first_name", "last_name", "organization", "country_id", "role_id"],
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


class AssignUserRoleToUser(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data

        if not check_super_admin(self.request.user):
            raise action_authorization_exception("Unauthorized to perform action")

        check_required_fields(data, ["user_key", "role_id"])

        try:
            role = UserRole.objects.get(id=data["role_id"])
            user = User.objects.get(user_key=data["user_key"])
            user.role_id = role.id
            user.updated_on = make_aware(datetime.datetime.now())
            user.save()

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Role assigned to user successfully",
                },
                safe=False,
            )
        except UserRole.DoesNotExist:
            raise non_existing_data_exception("User role")
        except User.DoesNotExist:
            raise non_existing_data_exception("User")


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

        user = User.objects.filter(user_key=data["user_key"]).values(
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

        try:
            user = user[0]
        except IndexError:
            raise non_existing_data_exception("User")

        return JsonResponse(
            {
                "status": "success",
                "detail": "User retrieved successfully",
                "data": user,
            },
            safe=False,
        )
