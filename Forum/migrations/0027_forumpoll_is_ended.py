# Generated by Django 4.2.1 on 2023-09-15 09:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Forum", "0026_forumpoll_forumpollchoices_forumpollvote"),
    ]

    operations = [
        migrations.AddField(
            model_name="forumpoll",
            name="is_ended",
            field=models.BooleanField(default=False),
        ),
    ]
