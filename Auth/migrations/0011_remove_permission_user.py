# Generated by Django 4.2.1 on 2023-06-05 18:52

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Auth", "0010_rename_modules_module_permission_module_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="permission",
            name="user",
        ),
    ]
