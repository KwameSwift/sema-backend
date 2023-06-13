from django.db import models

from Auth.models import User


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="blog_author",
    )
    blog_image_location = models.CharField(max_length=255, null=True, blank=True)
    blog_links = models.JSONField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    approved_and_published_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="approved_by",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Blog_Posts"


class BlogComment(models.Model):
    blog = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="blog",
    )
    comment = models.TextField(null=True, blank=True)
    commentor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="commentor",
    )
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Blog_Comments"
