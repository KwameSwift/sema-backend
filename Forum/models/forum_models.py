from django.db import models
from Auth.models import User


class Forum(models.Model):
    topic = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    tags = models.JSONField(blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_author",
    )
    forum_likers = models.ManyToManyField(
        User,
        related_name="forum_likers",
    )
    total_comments = models.IntegerField(default=0)
    total_likes = models.IntegerField(default=0)
    total_shares = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Forums"


class VirtualMeeting(models.Model):
    meeting_url = models.URLField()
    meeting_agenda = models.CharField(max_length=255, blank=True)
    scheduled_start_time = models.DateTimeField()
    scheduled_end_time = models.DateTimeField()
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="meeting_organizer",
    )
    attendees = models.ManyToManyField(
        User,
        related_name="virtual_meeting_attendees",
    )
    total_attendees = models.IntegerField(default=0)
    forum = models.ForeignKey(
        Forum,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_meeting_room",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Virtual_Meetings"


class ForumFile(models.Model):
    file_name = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    file_url = models.CharField(max_length=255, blank=True)
    file_key = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=255, blank=True)
    uploader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_file_uploader",
    )
    forum = models.ForeignKey(
        Forum,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_file",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Forum_Files"


class ForumComment(models.Model):
    forum = models.ForeignKey(
        Forum,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_comment",
    )
    comment = models.CharField(max_length=255, blank=True)
    parent_comment = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comment_parent_comment",
    )
    commentor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_commentor",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Forum_Comments"


class ChatRoom(models.Model):
    room_name = models.CharField(max_length=255)
    description = models.TextField()
    forum = models.ForeignKey(
        Forum,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_chat_room",
    )
    total_members = models.IntegerField(default=0)
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_room_creator",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Chat_Rooms"


class UserChatRoom(models.Model):
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="meeting_room_member",
    )
    membership_type = models.CharField(max_length=255, blank=True)
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users_meeting_room",
    )
    joined_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-joined_on",)
        db_table = "User_Chat_Rooms"


class SharedFile(models.Model):
    file_name = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    file_type = models.CharField(max_length=255, blank=True)
    file_url = models.CharField(max_length=255, blank=True)
    file_key = models.CharField(max_length=255, blank=True)
    uploader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="file_uploader",
    )
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="file_meeting_room",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Shared_Files"
