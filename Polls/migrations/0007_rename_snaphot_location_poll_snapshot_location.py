# Generated by Django 4.2.1 on 2023-07-15 08:55

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Polls", "0006_poll_snaphot_location_poll_snapshot_key"),
    ]

    operations = [
        migrations.RenameField(
            model_name="poll",
            old_name="snaphot_location",
            new_name="snapshot_location",
        ),
    ]
