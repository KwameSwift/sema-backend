# Generated by Django 4.2.1 on 2023-06-18 10:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("Polls", "0003_poll_voters"),
    ]

    operations = [
        migrations.AddField(
            model_name="pollchoices",
            name="voter",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="poll_voter",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]