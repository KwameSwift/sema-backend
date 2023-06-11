from django.db import models

from Auth.models import User


class UserDocuments(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="documents_owner",
    )

    document_location = models.CharField(max_length=255, blank=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_on",)
        db_table = "User_Documents"
