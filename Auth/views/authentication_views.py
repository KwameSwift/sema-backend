import datetime

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.utils.timezone import make_aware
# from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
# from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from Auth.models import User
from helpers.email_sender import send_another_email, send_email
from helpers.status_codes import (PasswordMismatch, UserAlreadyExists,
                                  UserDoesNotExist, WrongCredentials)
from helpers.validations import check_required_fields


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data

        check_required_fields(data, ["email"])

        if "password" in data:
            check_required_fields(data, ["password", "confirm_password"])
            if data["password"] == data["confirm_password"]:
                data["password"] = make_password(data["password"])
                data["account_type"] = "Contnent Creator"
            else:
                raise PasswordMismatch()
        else:
            data["account_type"] = "Guest"
        try:
            User.objects.get(email=data[("email")])
            raise UserAlreadyExists()
        except User.DoesNotExist:
            user = User.objects.create(**data)

        # Send welcome mail to user
        new_line = "\n"
        email = data["email"]
        account_type = data["account_type"]
        message = (
            f"Hi, {email}. {new_line}"
            f"Thank you for signing up on Sema as a {account_type}. {new_line}"
            f"We hope you have a wonderful time {new_line}{new_line}"
            f"The Sema Team"
        )
        send_email(data["email"], "Welcome to Sema", message)
        
        
        refresh = RefreshToken.for_user(user)

        # Construct user object with tokens and necessary details
        tokens = {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
        }
        
        return JsonResponse(
            {
                "status": "success",
                "detail": "User registered successfully",
                "data": user.user_key,
                "tokens": tokens
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

                # Construct user object with tokens and necessary details
                data = {
                    "refresh_token": str(refresh),
                    "access_token": str(refresh.access_token),
                }

                settings.TIME_ZONE
                naive_datetime = datetime.datetime.now()
                aware_datetime = make_aware(naive_datetime)
                user.last_login = aware_datetime
                user.save()

                data["user"]["user_key"] = (user.user_key,)
                data["user"]["role_id"] = (user.role_id,)
                data["user"]["role_name"] = (user.role.name,)
                data["user"]["email"] = (user.email,)
                data["user"]["account_type"] = (user.account_type,)
                data["user"]["is_admin"] = user.is_admin

                return JsonResponse(
                    {"status": "success", "detail": "Login successful", "data": data},
                    safe=False,
                )
            else:
                raise WrongCredentials()
        except User.DoesNotExist:
            raise UserDoesNotExist()
        

class TestEmailService(APIView):
    def post(self, request, *args, **kwargs):
        print("Request is here")
        
        email = send_another_email()
        print(email)
        return JsonResponse({'response': 'success'}, safe=False)
