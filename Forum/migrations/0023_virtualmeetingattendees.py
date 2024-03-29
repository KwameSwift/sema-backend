# Generated by Django 4.2.1 on 2023-09-13 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("Forum", "0022_remove_virtualmeeting_attendees"),
    ]

    operations = [
        migrations.CreateModel(
            name="VirtualMeetingAttendees",
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
                ("first_name", models.CharField(blank=True, max_length=255)),
                ("last_name", models.CharField(blank=True, max_length=255)),
                ("email", models.CharField(blank=True, max_length=255)),
                ("mobile_number", models.CharField(blank=True, max_length=255)),
                ("city", models.CharField(blank=True, max_length=255)),
                ("country", models.CharField(blank=True, max_length=255)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(blank=True, null=True)),
                (
                    "meeting",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="virtual_meeting",
                        to="Forum.virtualmeeting",
                    ),
                ),
            ],
            options={
                "db_table": "Virtual_Meeting_Attendees",
                "ordering": ("-created_on",),
            },
        ),
    ]
