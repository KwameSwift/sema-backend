# Generated by Django 4.2.1 on 2023-09-11 11:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Forum", "0020_alter_chatroommessages_media_files"),
    ]

    operations = [
        migrations.AddField(
            model_name="forumfile",
            name="file_category",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
