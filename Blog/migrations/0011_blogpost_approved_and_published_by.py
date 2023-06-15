# Generated by Django 4.2.1 on 2023-06-13 15:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("Blog", "0010_blogpost_blog_links"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="approved_and_published_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="approved_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]