# Generated by Django 4.2.1 on 2023-09-03 09:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Forum", "0019_chatroommessages"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatroommessages",
            name="media_files",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
