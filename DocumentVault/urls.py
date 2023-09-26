from django.urls import path

from DocumentVault.views.document_vault_views import (
    UploadDocumentToVault,
    DeleteVaultDocument,
    GetAllDocumentsInVault,
)

urlpatterns = [
    # Forums
    path(
        "upload-vault-document/",
        UploadDocumentToVault.as_view(),
        name="Upload Document To Vault",
    ),
    path(
        "delete-vault-document/<slug:document_id>/",
        DeleteVaultDocument.as_view(),
        name="Delete Vault Document",
    ),
    path(
        "get-all-vault-documents/<int:page_number>/",
        GetAllDocumentsInVault.as_view(),
        name="Get All Documents In Vault",
    ),
]
