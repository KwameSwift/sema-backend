from django.db import models

from Auth.models import User, Country


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
    forum_members = models.ManyToManyField(
        User,
        related_name="forum_members",
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_approver",
    )
    header_key = models.CharField(max_length=255, blank=True)
    header_image = models.CharField(max_length=255, blank=True)
    total_likes = models.IntegerField(default=0)
    total_comments = models.IntegerField(default=0)
    total_members = models.IntegerField(default=0)
    total_shares = models.IntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    approved_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    is_declined = models.BooleanField(default=False)
    decline_comment = models.CharField(max_length=255, blank=True)
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


class VirtualMeetingAttendees(models.Model):
    meeting = models.ForeignKey(
        VirtualMeeting,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="virtual_meeting",
    )
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    mobile_number = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attendee_country",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Virtual_Meeting_Attendees"


class ForumFile(models.Model):
    file_name = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    file_url = models.CharField(max_length=255, blank=True)
    file_key = models.CharField(max_length=255, blank=True)
    file_category = models.CharField(max_length=255, blank=True)
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
    total_messages = models.IntegerField(default=0)
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


class ForumRequest(models.Model):
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="join_requester",
    )
    forum = models.ForeignKey(
        Forum,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="request_forum",
    )
    is_approved = models.BooleanField(default=False)
    is_declined = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Forum_Requests"


class ChatRoomMessages(models.Model):
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_room_messages",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="message_sender",
    )
    message = models.TextField(blank=True)
    is_media = models.BooleanField(default=False)
    file_type = models.CharField(max_length=255, blank=True)
    media_files = models.JSONField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Chat_Room_Messages"


class ForumPoll(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_poll_author",
    )
    forum = models.ForeignKey(
        Forum,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_poll",
    )
    question = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(auto_now_add=False, null=True, blank=True)
    end_date = models.DateField(auto_now_add=False, null=True, blank=True)
    is_ended = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("-created_on",)
        db_table = "Forum_Polls"


class ForumPollChoices(models.Model):
    forum_poll = models.ForeignKey(
        ForumPoll,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_poll",
    )
    choice = models.CharField(max_length=255, null=True, blank=True)
    votes = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("created_on",)
        db_table = "Forum_Poll_Choices"


class ForumPollVote(models.Model):
    forum_poll = models.ForeignKey(
        ForumPoll,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_poll_for_choice",
    )
    poll_choice = models.ForeignKey(
        ForumPollChoices,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_poll_choice",
    )
    voter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_poll_choice_voter",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("created_on",)
        db_table = "Forum_Poll_Votes"


class ForumDiscussion(models.Model):
    forum = models.ForeignKey(
        Forum,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_discussion",
    )
    comment = models.TextField()
    commentor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_commentor",
    )
    is_forum_admin = models.BooleanField(default=False)
    total_likes = models.IntegerField(default=0)
    forum_comment_likers = models.ManyToManyField(
        User,
        related_name="forum_comment_likers",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        ordering = ("created_on",)
        db_table = "Forum_Discussion"
