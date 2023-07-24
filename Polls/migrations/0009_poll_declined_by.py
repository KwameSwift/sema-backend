# Generated by Django 4.2.1 on 2023-07-24 08:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("Polls", "0008_poll_is_declined"),
    ]

    operations = [
        migrations.AddField(
            model_name="poll",
            name="declined_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="poll_decliner",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]