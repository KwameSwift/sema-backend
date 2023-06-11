from django.db import models

from Auth.models.user_model import UserRole


class Module(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(
        auto_now=False,
        null=True,
    )

    class Meta:
        db_table = "Modules"


class Permission(models.Model):
    role = models.ForeignKey(
        UserRole,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="user_role",
    )
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, blank=True, null=True, related_name="module"
    )
    access_level = models.IntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(
        auto_now=False,
        null=True,
    )

    class Meta:
        db_table = "Permission_Manager"
