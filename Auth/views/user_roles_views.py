import datetime

from django.http import JsonResponse
from django.utils.timezone import make_aware
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models.user_model import UserRole
from helpers.functions import paginate_data
from helpers.status_codes import duplicate_data_exception, non_existing_data
from helpers.validations import check_required_fields


class AddUserRoleView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data

        check_required_fields(data, ["name"])

        try:
            UserRole.objects.get(name=data["name"])
            raise duplicate_data_exception("User role")
        except UserRole.DoesNotExist:
            UserRole.objects.create(**data)

            return JsonResponse(
                {"status": "success", "detail": "User role added successfully"},
                safe=False,
            )


class DeleteUserRoleView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        role_id = self.kwargs.get("role_id")

        try:
            role = UserRole.objects.get(id=role_id)
            role.delete()
            return JsonResponse(
                {"status": "success", "detail": "User role deleted successfully"},
                safe=False,
            )
        except UserRole.DoesNotExist:
            raise non_existing_data("User role")


class UpdateUserRoleView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        role_id = self.kwargs.get("role_id")
        data = request.data

        try:
            role = UserRole.objects.get(id=role_id)
            role.name = data.get("name")
            role.updated_on = make_aware(datetime.datetime.now())
            role.save()
            return JsonResponse(
                {"status": "success", "detail": "User role updated successfully"},
                safe=False,
            )
        except UserRole.DoesNotExist:
            raise non_existing_data("User role")


class GetAllUserRolesView(APIView):
    def get(self, request, *args, **kwargs):
        page_number = self.kwargs.get("page_number")

        user_roles = UserRole.objects.all().values().order_by("-created_on")

        data = paginate_data(user_roles, page_number, 10)

        return JsonResponse(data, safe=False)


class GetSingleUserRoleView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        role_id = self.kwargs.get("role_id")

        try:
            role = UserRole.objects.filter(id=role_id).values()
            return JsonResponse(
                {
                    "status": "success",
                    "detail": "User role retrieved successfully",
                    "data": role[0],
                },
                safe=False,
            )
        except IndexError:
            raise non_existing_data("User role")
