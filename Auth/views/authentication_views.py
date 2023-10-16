import datetime

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.http import JsonResponse
from django.utils.timezone import make_aware
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from Auth.models import User
from Auth.models.permissions_model import Permission
from Auth.models.user_model import UserRole, Country
from Blog.models.blog_model import BlogPost
from helpers.email_sender import send_email, welcome_message
from helpers.status_codes import (
    PasswordMismatch,
    WrongCode,
    WrongCredentials,
    WrongPassword,
    cannot_perform_action,
    duplicate_data_exception,
    non_existing_data_exception,
    invalid_data,
)
from helpers.validations import (
    check_required_fields,
    generate_password_reset_code,
    is_email,
)


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data

        check_required_fields(data, ["first_name", "last_name"])
        try:
            if "email" in data:
                User.objects.get(email=data["email"])
                raise duplicate_data_exception("User with email")
        except User.DoesNotExist:
            if "password" in data:
                check_required_fields(data, ["email"])
                user_role = UserRole.objects.get(name="Content Creator")
                check_required_fields(
                    data,
                    [
                        "password",
                        "confirm_password",
                        "organization",
                        "country_id",
                        "mobile_number",
                    ],
                )
                if data["password"] == data["confirm_password"]:
                    data["password"] = make_password(data["password"])
                    data["account_type"] = "Content Creator"
                    data.pop("confirm_password", None)
                else:
                    raise PasswordMismatch()
            else:
                check_required_fields(data, ["country_id", "mobile_number"])
                if "country_id" in data:
                    try:
                        country = Country.objects.get(id=data["country_id"])
                        if "mobile_number" in data:
                            login_field = str(country.calling_code) + str(
                                data["mobile_number"]
                            ).lstrip("0")
                            data["mobile_login_field"] = login_field
                    except Country.DoesNotExist:
                        raise non_existing_data_exception("Country")
                user_role = UserRole.objects.get(name="Guest")
                data["account_type"] = "Guest"

            data["role_id"] = user_role.id
            user = User.objects.create(**data)

            # Send welcome mail to user
            send_email(data["email"], "Welcome to Sema", welcome_message)

            refresh = RefreshToken.for_user(user)

            # Construct a user object with tokens and necessary details
            data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {},
            }

            data["user"]["user_key"] = user.user_key
            data["user"]["role_id"] = user.role_id
            permissions = list(
                Permission.objects.filter(role_id=user.role_id).values(
                    "id", "module_id", "module__name", "access_level"
                )
            )
            try:
                data["user"]["role_name"] = user.role.name
            except AttributeError:
                data["user"]["role_name"] = None
            data["user"]["email"] = user.email
            data["user"]["account_type"] = user.account_type
            data["user"]["is_admin"] = user.is_admin
            data["permissions"] = permissions

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "User registered successfully",
                    "data": data,
                },
                safe=False,
            )


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        check_required_fields(data, ["email", "password"])

        try:
            user = User.objects.get(email=data["email"])
            if user.check_password(data["password"]):
                # Generate a token for authenticated user
                refresh = RefreshToken.for_user(user)

                liked_blogs = user.blog_likers.all()
                blog_ids = [blog.id for blog in liked_blogs]

                liked_discussions = user.forum_comment_likers.all()
                discussion_ids = [discussion.id for discussion in liked_discussions]

                # Construct a user object with tokens and necessary details
                data = {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": {},
                }

                naive_datetime = datetime.datetime.now()
                aware_datetime = make_aware(naive_datetime)
                user.last_login = aware_datetime
                user.save()

                data["user"]["user_key"] = user.user_key
                data["user"]["role_id"] = user.role_id

                permissions = list(
                    Permission.objects.filter(role_id=user.role_id).values(
                        "id", "module_id", "module__name", "access_level"
                    )
                )
                try:
                    data["user"]["role_name"] = user.role.name
                except AttributeError:
                    data["user"]["role_name"] = None
                data["user"]["email"] = user.email
                data["user"]["account_type"] = user.account_type
                data["user"]["is_admin"] = user.is_admin
                data["liked_blogs"] = blog_ids
                data["liked_discussions"] = discussion_ids
                data["permissions"] = permissions

                return JsonResponse(
                    {"status": "success", "detail": "Login successful", "data": data},
                    safe=False,
                )
            else:
                raise WrongCredentials()
        except User.DoesNotExist:
            raise non_existing_data_exception("User with email")


class GuestLoginView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        check_required_fields(data, ["login_type"])

        if data["login_type"] == "Email":
            check_required_fields(data, ["email"])
            try:
                user = User.objects.get(email=data["email"])
            except User.DoesNotExist:
                raise non_existing_data_exception("User with email")
        elif data["login_type"] == "Mobile":
            check_required_fields(data, ["mobile_number"])
            try:
                user = User.objects.get(mobile_login_field=data["mobile_number"])
            except User.DoesNotExist:
                raise non_existing_data_exception("User with mobile number")
        else:
            raise invalid_data("Can only login via Email or Mobile")

        if user.account_type == "Guest":
            refresh = RefreshToken.for_user(user)

            liked_blogs = user.blog_likers.all()
            blog_ids = [blog.id for blog in liked_blogs]

            liked_discussions = user.forum_comment_likers.all()
            discussion_ids = [discussion.id for discussion in liked_discussions]

            # Construct a user object with tokens and necessary details
            data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {},
            }

            naive_datetime = datetime.datetime.now()
            aware_datetime = make_aware(naive_datetime)
            user.last_login = aware_datetime
            user.save()

            data["user"]["user_key"] = user.user_key
            data["user"]["role_id"] = user.role_id

            permissions = list(
                Permission.objects.filter(role_id=user.role_id).values(
                    "id", "module_id", "module__name", "access_level"
                )
            )
            try:
                data["user"]["role_name"] = user.role.name
            except AttributeError:
                data["user"]["role_name"] = None
            data["user"]["email"] = user.email
            data["user"]["account_type"] = user.account_type
            data["user"]["is_admin"] = user.is_admin
            data["liked_blogs"] = blog_ids
            data["liked_discussions"] = discussion_ids
            data["permissions"] = permissions

            return JsonResponse(
                {"status": "success", "detail": "Login successful", "data": data},
                safe=False,
            )
        else:
            raise cannot_perform_action("Account is not a Guest Account")


class SendResetPasswordMailView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        check_required_fields(data, ["email"])

        try:
            user = User.objects.get(email=data["email"])

            if user.account_type == "Guest":
                raise cannot_perform_action(
                    "The email entered signed up as a Guest account"
                )

            reset_code = generate_password_reset_code()
            user.password_reset_code = reset_code
            user.save()
            new_line = "\n"
            double_new_line = "\n\n"
            message = (
                f"Hi, {user.first_name}.{new_line}"
                f"You have requested to reset your password."
                f"Please use the code below to reset your password: {new_line}"
                f"{reset_code}"
                f"{double_new_line}The Sema Team"
            )

            send_email(user.email, "Password Reset", message)

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Password reset email sent successfully",
                },
                safe=False,
            )
        except User.DoesNotExist:
            raise non_existing_data_exception("User with email")


class VerifyPasswordResetCode(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data

        check_required_fields(data, ["reset_code", "email"])

        try:
            User.objects.get(
                password_reset_code=data["reset_code"], email=data["email"]
            )
            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Code verified successfully",
                },
                safe=False,
            )

        except User.DoesNotExist:
            raise WrongCode()


class PasswordResetView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data

        check_required_fields(data, ["email", "new_password", "confirm_password"])

        try:
            user = User.objects.get(email=data["email"])
            if data["new_password"] == data["confirm_password"]:
                user.password = make_password(data["new_password"])
                user.password_reset_code = None
                user.save()

                return JsonResponse(
                    {
                        "status": "success",
                        "detail": "Password reset successful",
                    },
                    safe=False,
                )
            else:
                raise PasswordMismatch()
        except User.DoesNotExist:
            raise WrongCode()


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        data = request.data
        user = self.request.user

        check_required_fields(
            data, ["old_password", "new_password", "confirm_password"]
        )
        try:
            user = User.objects.get(email=user.email)
            if user.check_password(data["old_password"]):
                if data["new_password"] == data["confirm_password"]:
                    user.password = make_password(data["new_password"])
                    user.save()

                    return JsonResponse(
                        {
                            "status": "success",
                            "detail": "Password changed successfully",
                        },
                        safe=False,
                    )
                else:
                    raise PasswordMismatch()
            else:
                raise WrongPassword()
        except User.DoesNotExist:
            raise non_existing_data_exception("User")


class CallBack(APIView):
    def get(self, request, *args, **kwargs):
        message = request.data
        send_email("charlestontaylor09@gmail.com", "Redirect URL", message)

        return JsonResponse(
            {
                "status": "success",
                "detail": "Password changed successfully",
            },
            safe=False,
        )
