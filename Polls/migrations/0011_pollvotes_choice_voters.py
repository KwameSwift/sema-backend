# Generated by Django 4.2.1 on 2023-07-03 21:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("Polls", "0010_poll_is_ended"),
    ]

    operations = [
        migrations.AddField(
            model_name="pollvotes",
            name="choice_voters",
            field=models.ManyToManyField(
                related_name="poll_choice_voter", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
