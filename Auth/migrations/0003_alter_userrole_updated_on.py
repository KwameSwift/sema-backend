# Generated by Django 4.2.1 on 2023-06-05 09:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Auth", "0002_user_account_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userrole",
            name="Updated_on",
            field=models.DateTimeField(null=True),
        ),
    ]