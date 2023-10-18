import uuid
from django.db import models

from Auth.models import User


class Document(models.Model):
    document_id = models.UUIDField(
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
    )
    file_name = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    file_url = models.CharField(max_length=255, blank=True)
    file_key = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="vault_document_owner",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Documents_Vault"
