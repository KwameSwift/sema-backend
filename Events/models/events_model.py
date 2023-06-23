from django.db import models

from Auth.models import User


# Events model
class Events(models.Model):
    event_name = models.CharField(max_length=255, null=True, blank=True)
    venue = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    event_links = models.JSONField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="events_owner",
    )
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="events_approved_by",
    )
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("-start_date",)
        db_table = "Events"
