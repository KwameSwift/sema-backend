# Generated by Django 4.2.1 on 2023-06-11 16:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Auth", "0016_user_profile_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserDocuments",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "document_location",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents_owner",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "User_Documents",
                "ordering": ("created_on",),
            },
        ),
    ]
