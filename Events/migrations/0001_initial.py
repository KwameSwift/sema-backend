# Generated by Django 4.2.1 on 2023-06-11 19:50

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Events",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("event_name", models.CharField(blank=True, max_length=255, null=True)),
                ("venue", models.CharField(blank=True, max_length=255, null=True)),
                ("location", models.CharField(blank=True, max_length=255, null=True)),
                ("start_date", models.DateField(blank=True, null=True)),
                (
                    "event_image",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("end_date", models.DateField(blank=True, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("created_on", models.DateField(auto_now_add=True)),
                ("updated_on", models.DateField(blank=True, null=True)),
            ],
            options={
                "db_table": "Events",
                "ordering": ("-start_date",),
            },
        ),
    ]