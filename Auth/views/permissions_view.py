import datetime

from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models.permissions_model import Module, Permission
from Auth.models.user_model import User, UserRole
from helpers.functions import aware_datetime, paginate_data
from helpers.status_codes import (cannot_perform_action,
                                  duplicate_data_exception,
                                  non_existing_data_exception)
from helpers.validations import check_required_fields


class AssignRolesView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data

        check_required_fields(data, ["role_id", "user_key"])

        try:
            user = User.objects.get(user_key=data["user_key"])
            role = UserRole.objects.get(id=data["role_id"])
            user.role_id = role.id
            user.save()

            return JsonResponse(
                {"status": "success", "detail": "Role assigned to user successfully"},
                safe=False,
            )
        except UserRole.DoesNotExist:
            raise non_existing_data_exception("User role")
        except User.DoesNotExist:
            raise non_existing_data_exception("User")


class DeleteUserRole(APIView):
    """
    This API view contains a delete function that deletes a user role in
    the database.
    It requires users to be authenticated before performing this task.

    Handles DELETE requests and returns a Response.
        Args:
            request (Request): The HTTP request object.
            role_id (URL param): The ID of the role to be deleted

        Returns:
            Response: A JsonResponse with data  and a status code indicating the role
            was deleted successfully or otherwise.
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        role_id = self.kwargs["role_id"]

        try:
            # Fetch role to be deleted from the database
            role = UserRole.objects.get(id=role_id)

            # If role name is Super Admin, raise error that it is not deletable
            if role.name == "Super Admin":
                raise cannot_perform_action("Cannot delete Super Admin role")

            # Else delete the role
            role.delete()
            # Return response to user
            return JsonResponse(
                {"status": "success", "detail": "Role deleted successfully"},
                safe=False,
            )
        except UserRole.DoesNotExist:
            # Raise exception if role does not exist
            raise non_existing_data_exception("User role")


class AddUserRole(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        module_data = request.data.get("module_data")
        name = request.data.get("name")

        # Check for the existence of all required fields
        check_required_fields(request.data, ["module_data", "name"])
        try:
            # Check if user role with name already exists
            UserRole.objects.get(name=name)
            # Raise exception if data exists
            raise duplicate_data_exception("User role")
        except UserRole.DoesNotExist:
            # If user role does not exist, create ir
            user_role = UserRole.objects.create(name=name)

        for data in module_data:
            try:
                # For each module assigned to the user role,
                # create a permission object for it
                Module.objects.get(id=data["module_id"])
                details = {
                    "role_id": user_role.id,
                    "module_id": data["module_id"],
                    "access_level": data["access_level"],
                }
                # Save permission (access level) in DB
                Permission.objects.create(**details)
            except Module.DoesNotExist:
                # Except that module does not exist, raise an exception
                raise non_existing_data_exception("Module")
        # Return response to user
        return JsonResponse(
            {"status": "success", "detail": "Role added successfully"},
            safe=False,
        )


class GetAllUserRoles(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        page_number = self.kwargs["page_number"]
        data = {}
        user_roles = Permission.objects.filter(access_level__in=[1, 2]).values(
            "id",
            "module__name",
            "module_id",
            "role_id",
            "role__name",
            "access_level",
        )
        for role in user_roles:
            new_role = role.copy()
            new_role.pop("role__name")
            if data.get(role["role__name"]):
                data[role["role__name"]] = [*data.get(role["role__name"]), new_role]
            else:
                data[role["role__name"]] = [new_role]
        list_res = [{key: val} for key, val in data.items()]
        # Paginate the data
        data = paginate_data(list_res, page_number, 10)

        # Send response to user
        return JsonResponse(data, safe=False)


class GetSingleRole(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        role_id = self.kwargs["role_id"]
        user_role = UserRole.objects.filter(id=role_id).values().first()

        user_permissions = Permission.objects.filter(role_id=role_id).values(
            "id", "module_id", "module__name", "access_level"
        )
        user_role["permissions"] = list(user_permissions)
        # Send response to user
        return JsonResponse(
            {
                "status": "success",
                "detail": "Role updated successfully",
                "data": user_role,
            },
            safe=False,
        )


class UpdateUserRole(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        role_id = self.kwargs["role_id"]
        module_data = request.data.get("module_data")
        name = request.data.get("name")

        # Check if data to be updated with contains "role_title"
        if "name" in request.data:
            name = request.data["name"]
            try:
                # Check if that role title does not exist already
                role = UserRole.objects.get(name=name)
                # Raise exception if title exists
                raise duplicate_data_exception("User role")
            except UserRole.DoesNotExist:
                # Update the role if title does not exist
                role.name = name
                role.updated_on = aware_datetime(datetime.datetime.now())
                role.save()

        for data in module_data:
            try:
                # Get all permissions assigned to modules for that user role
                permission = Permission.objects.get(
                    module_id=data["module_id"], role_id=role_id
                )
                # If there are permissions to be updated, it is done and saved
                permission.access_level = data["access_level"]
                permission.updated_on = aware_datetime(datetime.datetime.now())
                permission.save()
            except Permission.DoesNotExist:
                # If any permission does not exist, raise an exception
                raise non_existing_data_exception("Permission")

        # Return response to user
        return JsonResponse(
            {"status": "success", "detail": "Role updated successfully"},
            safe=False,
        )


class AddModuleView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data

        check_required_fields(data, ["name"])

        try:
            Module.objects.get(name=data["name"])
            raise duplicate_data_exception("Module")
        except Module.DoesNotExist:
            Module.objects.create(**data)

            return JsonResponse(
                {"status": "success", "detail": "Module added successfully"},
                safe=False,
            )
