# Generated by Django 4.2.1 on 2023-06-18 10:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Polls", "0006_pollvotes"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pollchoices",
            name="votes",
        ),
    ]