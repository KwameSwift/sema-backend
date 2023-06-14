from django.db import models

from Auth.models import User
from Blog.models.blog_model import BlogPost
from Events.models.events_model import Events


class UserDocuments(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="document_owner",
    )
    document_type = models.CharField(max_length=255, blank=True, null=True)
    document_location = models.CharField(max_length=255, blank=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_on",)
        db_table = "User_Documents"


class BlogDocuments(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="blog_document_owner",
    )
    blog = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="blog_document",
    )
    document_location = models.CharField(max_length=255, blank=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_on",)
        db_table = "Blog_Documents"


class EventDocuments(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="event_document_owner",
    )
    event = models.ForeignKey(
        Events,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="event_document",
    )
    document_location = models.CharField(max_length=255, blank=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_on",)
        db_table = "Event_Documents"
