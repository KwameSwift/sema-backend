# Generated by Django 4.2.1 on 2023-07-04 17:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("Polls", "0013_poll_description_poll_title_delete_pollvotes"),
    ]

    operations = [
        migrations.AddField(
            model_name="poll",
            name="approved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="poll_approver",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # migrations.DeleteModel(
        #     name="PollVotes",
        # ),
    ]