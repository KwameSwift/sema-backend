# Generated by Django 4.2.1 on 2023-06-05 09:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Auth", "0003_alter_userrole_updated_on"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="Auth.userrole",
            ),
        ),
    ]