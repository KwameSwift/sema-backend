from django.db import models

from Auth.models import User


# Polls model
class Poll(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="poll_author",
    )
    voters = models.ManyToManyField(
        User,
        related_name="poll_voters",
    )
    question = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Polls"


# Poll choices
class PollChoices(models.Model):
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="poll",
    )
    choice = models.CharField(max_length=255, null=True, blank=True)
    votes = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("created_on",)
        db_table = "Poll_Choices"
