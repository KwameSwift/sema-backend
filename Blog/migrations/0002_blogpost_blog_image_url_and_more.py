# Generated by Django 4.2.1 on 2023-06-11 07:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Blog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="blog_image_url",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="bloge_image_location",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
