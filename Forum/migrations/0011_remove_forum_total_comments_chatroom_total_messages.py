# Generated by Django 4.2.1 on 2023-08-22 13:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Forum", "0010_delete_forumcomment"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="forum",
            name="total_comments",
        ),
        migrations.AddField(
            model_name="chatroom",
            name="total_messages",
            field=models.IntegerField(default=0),
        ),
    ]
