# Generated by Django 4.2.1 on 2023-06-10 13:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Auth", "0011_remove_permission_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="updated_on",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
