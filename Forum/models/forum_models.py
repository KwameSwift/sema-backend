from django.db import models
from Auth.models import User


class MeetingRoom(models.Model):
    room_name = models.CharField(max_length=255)
    description = models.TextField()
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="meeting_room_creator",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Meeting_Rooms"


class UserMeetingRoom(models.Model):
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="meeting_room_member",
    )
    meeting_room = models.ForeignKey(
        MeetingRoom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users_meeting_room",
    )
    joined_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-joined_on",)
        db_table = "User_Meeting_Rooms"


class Chat(models.Model):
    content = models.TextField()
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="message_sender",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    meeting_room = models.ForeignKey(
        MeetingRoom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chats_meeting_room",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Chats"


class VirtualMeeting(models.Model):
    meeting_url = models.URLField()
    scheduled_start_time = models.DateTimeField()
    end_time = models.DateTimeField()
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
    meeting_room = models.ForeignKey(
        MeetingRoom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="virtual_meeting_room",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Virtual_Meetings"


class SharedFile(models.Model):
    file_name = models.CharField(max_length=255)
    description = models.TextField()
    file_url = models.CharField(max_length=255, null=True, blank=True)
    file_key = models.CharField(max_length=255, null=True, blank=True)
    uploader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="file_uploader",
    )
    upload_date = models.DateTimeField(auto_now_add=True)
    meeting_room = models.ForeignKey(
        MeetingRoom,
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
