# Generated by Django 4.2.1 on 2023-06-10 13:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Auth", "0013_country_remove_user_country"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="country",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="Auth.country",
            ),
        ),
    ]
