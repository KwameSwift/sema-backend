# Generated by Django 4.2.1 on 2023-06-14 07:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Blog", "0011_blogpost_approved_and_published_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="description",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
