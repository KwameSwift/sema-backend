# Generated by Django 4.2.1 on 2023-06-16 13:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Blog", "0019_rename_blog_links_blogpost_reference_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="cover_image",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]