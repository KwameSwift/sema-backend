# Generated by Django 4.2.1 on 2023-06-14 15:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Events", "0004_events_approved_by_events_is_approved"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="events",
            name="event_image",
        ),
    ]