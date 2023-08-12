# Generated by Django 4.2.1 on 2023-08-10 10:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("Forum", "0003_forum_tags_forumfile_file_type_sharedfile_file_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatroom",
            name="forum",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="forum_chat_room",
                to="Forum.forum",
            ),
        ),
        migrations.AlterField(
            model_name="chatroom",
            name="creator",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="chat_room_creator",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
