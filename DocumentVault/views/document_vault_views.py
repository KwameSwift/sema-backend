import json
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from DocumentVault.models import Document
from helpers.azure_file_handling import create_vault_document, delete_blob
from helpers.functions import paginate_data
from helpers.status_codes import (
    action_authorization_exception,
    non_existing_data_exception,
)
from helpers.validations import check_permission


class UploadDocumentToVault(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data
        files = request.FILES.getlist("files[]")

        if not check_permission(user, "Documents Vault", [2]):
            raise action_authorization_exception(
                "Unauthorized to upload files to vault"
            )

        if files:
            files = data.pop("files[]", None)

        data = json.dumps(data)
        data = json.loads(data)

        document_urls = create_vault_document(files, user, data.get("description"))

        return JsonResponse(
            {
                "status": "success",
                "detail": "Files uploaded successfully",
                "data": document_urls,
            },
            safe=False,
        )


class DeleteVaultDocument(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        document_id = self.kwargs["document_id"]
        user = self.request.user

        if not check_permission(user, "Documents Vault", [2]):
            raise action_authorization_exception(
                "Unauthorized to delete files from vault"
            )

        try:
            document = Document.objects.get(document_id=document_id)

            if not document.owner == user or not user.role.name == "Super Admin":
                raise action_authorization_exception(
                    "Unauthorized to delete this file from vault"
                )

            container = f"{document.owner.first_name}-{document.owner.last_name}"
            delete_blob(container.lower(), document.file_key)

            document.delete()

            return JsonResponse(
                {"status": "success", "detail": "Document deleted successfully"},
                safe=False,
            )

        except Document.DoesNotExist:
            raise non_existing_data_exception("Document")


class GetAllDocumentsInVault(APIView):
    def get(self, request, *args, **kwargs):
        page_number = self.kwargs["page_number"]
        documents = (
            Document.objects.all()
            .values(
                "document_id",
                "file_name",
                "description",
                "file_url",
                "file_type",
                "owner__first_name",
                "owner__last_name",
                "owner__is_verified",
                "owner__organization",
                "created_on",
            )
            .order_by("-created_on")
        )

        data = paginate_data(list(documents), page_number, 20)
        return JsonResponse(
            data,
            safe=False,
        )


class GetMyDocumentsInVault(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        page_number = self.kwargs["page_number"]

        documents = (
            Document.objects.filter(owner=user)
            .values(
                "document_id",
                "file_name",
                "description",
                "file_url",
                "file_type",
                "created_on",
            )
            .order_by("-created_on")
        )

        data = paginate_data(list(documents), page_number, 20)
        return JsonResponse(
            data,
            safe=False,
        )


class AdminGetAllDocumentsInVault(APIView):
    def get(self, request, *args, **kwargs):
        page_number = self.kwargs["page_number"]
        documents = (
            Document.objects.all()
            .values(
                "document_id",
                "file_name",
                "description",
                "file_url",
                "file_type",
                "owner__first_name",
                "owner__last_name",
                "owner__is_verified",
                "owner__organization",
                "created_on",
            )
            .order_by("-created_on")
        )

        data = paginate_data(list(documents), page_number, 20)
        return JsonResponse(
            data,
            safe=False,
        )
