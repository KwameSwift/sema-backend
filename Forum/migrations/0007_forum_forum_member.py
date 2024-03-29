# Generated by Django 4.2.1 on 2023-08-22 10:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("Forum", "0006_forum_header_image_forum_header_key"),
    ]

    operations = [
        migrations.AddField(
            model_name="forum",
            name="forum_member",
            field=models.ManyToManyField(
                related_name="forum_members", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
