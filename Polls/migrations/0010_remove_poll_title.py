# Generated by Django 4.2.1 on 2023-07-24 10:38

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Polls", "0009_poll_declined_by"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="poll",
            name="title",
        ),
    ]