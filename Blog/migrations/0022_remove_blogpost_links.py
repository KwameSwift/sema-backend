# Generated by Django 4.2.1 on 2023-06-23 07:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Blog", "0021_blogpost_links"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="blogpost",
            name="links",
        ),
    ]