# Generated by Django 4.2.1 on 2023-07-15 08:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Polls", "0005_remove_poll_comments_pollvote_comments"),
    ]

    operations = [
        migrations.AddField(
            model_name="poll",
            name="snaphot_location",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="poll",
            name="snapshot_key",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
