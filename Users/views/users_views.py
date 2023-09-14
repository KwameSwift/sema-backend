import json
import os
from datetime import datetime

from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models.user_model import User
from Blog.models.blog_model import BlogComment, BlogPost
from Events.models.events_model import Events
from Forum.forum_helper import (
    send_forum_join_request_approval_to_user,
    send_forum_join_request_decline_to_user,
    get_randomized_forums_suggestions,
)
from Forum.models import Forum, VirtualMeeting, ForumFile, ChatRoom, ForumRequest
from helpers.azure_file_handling import delete_blob, shorten_url, upload_profile_image
from helpers.functions import (
    convert_quill_text_to_normal_text,
    delete_file,
    local_file_upload,
    paginate_data,
    truncate_text,
    aware_datetime,
)
from helpers.status_codes import (
    action_authorization_exception,
    cannot_perform_action,
    non_existing_data_exception,
)
from helpers.validations import check_required_fields
from Polls.models.poll_models import Poll, PollVote
from Polls.poll_helper import retrieve_poll_with_choices
from Utilities.models.documents_model import UserDocuments

LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")


# View my profile
class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        usr = self.request.user
        user = (
            User.objects.filter(user_key=usr.user_key)
            .values(
                "user_key",
                "role__name",
                "email",
                "first_name",
                "last_name",
                "profile_image",
                "bio",
                "links",
                "organization",
                "mobile_number",
                "account_type",
                "country__calling_code",
                "country__flag",
                "country__name",
                "is_verified",
            )
            .first()
        )

        return JsonResponse(
            {
                "status": "success",
                "detail": "Profile retrieved successfully",
                "data": user,
            },
            safe=False,
        )


# Upload user documents
class UploadUserDocuments(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist("files")
        user = self.request.user

        local_file_path = os.environ.get("LOCAL_FILE_PATH")
        for file in files:
            full_directory = (
                f"{local_file_path}{user.first_name}_{user.last_name}/Documents"
            )
            file_path = local_file_upload(full_directory, file)

            new_event_image = {
                "owner": user,
                "document_type": "Personal Documents",
                "document_location": file_path,
            }

            UserDocuments.objects.create(**new_event_image)

        return JsonResponse(
            {"status": "success", "detail": "Documents uploaded successfully"},
            safe=False,
        )


# Get all blog posts created by a user
class GetUserBlogPosts(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        page_number = self.kwargs.get("page_number")
        data_type = self.kwargs.get("data_type")

        if user.account_type == "Guest":
            raise action_authorization_exception("Unauthorized to view Blogs")

        query = Q(author=user)
        if data_type == 1:
            query &= Q(is_approved=True)
        elif data_type == 2:
            query &= Q(is_approved=False)

        blog_posts = (
            BlogPost.objects.filter(query)
            .values(
                "id",
                "title",
                "content",
                "description",
                "total_likes",
                "total_shares",
                "cover_image",
                "censored_content",
                "is_abusive",
                "is_approved",
                "is_published",
                "approved_and_published_by__first_name",
                "approved_and_published_by__last_name",
                "reference",
                "author_id",
                "author__first_name",
                "author__last_name",
                "author__is_verified",
                "created_on",
            )
            .order_by("-created_on")
        )

        for blog_post in blog_posts:
            converted_text = convert_quill_text_to_normal_text(blog_post["content"])
            blog_post["preview_text"] = truncate_text(converted_text, 200)
            total_comments = BlogComment.objects.filter(
                blog_id=blog_post["id"]
            ).values()
            blog_post["total_comments"] = total_comments.count()

        data = paginate_data(blog_posts, page_number, 10)
        return JsonResponse(
            data,
            safe=False,
        )


# Delete Profile Image
class DeleteProfileImage(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        user = self.request.user

        if user.profile_image:
            delete_file(user.profile_image)
            user.profile_image = None
            user.save()
        else:
            raise cannot_perform_action("No image to delete")

        return JsonResponse(
            {"status": "success", "detail": "Profile image deleted successfully"},
            safe=False,
        )


# Get my statistics
class GetAuthorStatistics(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user

        total_blogs = BlogPost.objects.filter(author=user).count()
        total_events = Events.objects.filter(created_by=user).count()
        total_polls = Poll.objects.filter(author=user).count()
        total_forums = Forum.objects.filter(author=user).count()

        blogs = (
            BlogPost.objects.filter(author=user)
            .annotate(month=TruncMonth("created_on"))
            .values("month")
            .annotate(count=Count("id"))
        )
        blog_data = [
            {"month": entry["month"].strftime("%m-%Y"), "count": entry["count"]}
            for entry in blogs
        ]

        data = {
            "total_polls": total_polls,
            "total_blogs": total_blogs,
            "total_events": total_events,
            "total_forums": total_forums,
            "blog_data": blog_data,
        }

        return JsonResponse(
            {
                "status": "success",
                "detail": "Statistics retrieved successfully",
                "data": data,
            },
            safe=False,
        )


# Search blogs
class SearchMyBlogPosts(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        page_number = self.kwargs.get("page_number")
        data = request.data

        check_required_fields(data, ["search_query"])

        blog_posts = (
            BlogPost.objects.filter(
                Q(title__icontains=data["search_query"], author=user)
                | Q(description__icontains=data["search_query"], author=user)
                | Q(author__first_name__icontains=data["search_query"], author=user)
                | Q(author__last_name__icontains=data["search_query"], author=user)
            )
            .values(
                "id",
                "title",
                "content",
                "description",
                "is_approved",
                "total_likes",
                "total_shares",
                "is_published",
                "approved_and_published_by__first_name",
                "approved_and_published_by__last_name",
                "cover_image",
                "links",
                "censored_content",
                "is_abusive",
                "reference",
                "author_id",
                "author__first_name",
                "author__is_verified",
                "author__last_name",
                "created_on",
            )
            .order_by("-created_on")
        )

        for blog_post in blog_posts:
            total_comments = (
                BlogComment.objects.filter(blog_id=blog_post["id"])
                .values()
                .order_by("-created_on")
            )
            blog_post["total_comments"] = total_comments.count()

        data = paginate_data(blog_posts, page_number, 10)
        return JsonResponse(
            data,
            safe=False,
        )


# Update User Profile
class UpdateUserProfile(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data
        profile_image = request.FILES.get("profile_image")

        user = User.objects.get(user_key=user.user_key)
        container = f"{user.first_name}-{user.last_name}".lower()

        if profile_image:
            try:
                delete_blob(container, user.profile_image_key)
            except UserDocuments.DoesNotExist:
                pass
            url = upload_profile_image(profile_image, user)
            user.profile_image = url[0]
            user.profile_image_key = url[1]
            profile_image = data.pop("profile_image", None)
            user.save()

        data = json.dumps(data)
        data = json.loads(data)

        User.objects.filter(user_key=user.user_key).update(**data)

        return JsonResponse(
            {"status": "success", "detail": "User profile updated successfully"},
            safe=False,
        )


class GetMySinglePoll(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        poll_id = self.kwargs.get("poll_id")

        try:
            poll = Poll.objects.get(id=poll_id, author=user)
            poll_data = retrieve_poll_with_choices(poll.id)
            poll_data["poll_votes"] = list(
                (
                    PollVote.objects.filter(poll_id=poll.id).values(
                        "id",
                        "voter__first_name",
                        "voter__last_name",
                        "poll_choice__choice",
                        "poll_choice_id",
                        "comments",
                    )
                )
            )

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Poll retrieved successfully",
                    "data": poll_data,
                },
                safe=False,
            )
        except Poll.DoesNotExist:
            raise non_existing_data_exception("Poll")


class GetMyForums(APIView):
    def get(self, request, *args, **kwargs):
        page_number = self.kwargs.get("page_number")
        data_type = self.kwargs["data_type"]
        user = self.request.user

        query = Q(author=user)
        if data_type == 1:
            query &= Q(is_approved=True)
        elif data_type == 2:
            query &= Q(is_approved=False)
        elif data_type == 3:
            query &= Q(is_declined=True)

        try:
            forums = Forum.objects.filter(query).values(
                "id",
                "topic",
                "description",
                "tags",
                "author__first_name",
                "author__last_name",
                "author__profile_image",
                "author__is_verified",
                "author__organization",
                "total_likes",
                "total_shares",
                "is_public",
                "approved_on",
                "is_approved",
                "is_declined",
                "created_on",
            )
            for forum in forums:
                forum["virtual_meetings"] = list(
                    VirtualMeeting.objects.filter(forum_id=forum["id"]).values(
                        "id",
                        "meeting_agenda",
                        "meeting_url",
                        "scheduled_start_time",
                        "scheduled_end_time",
                        "organizer__first_name",
                        "organizer__last_name",
                        "total_attendees",
                    )
                )
                forum["files"] = list(
                    ForumFile.objects.filter(forum_id=forum["id"]).values(
                        "id", "description", "file_type", "file_url", "created_on"
                    )
                )
                forum["chat_rooms"] = list(
                    ChatRoom.objects.filter(forum_id=forum["id"]).values(
                        "id",
                        "room_name",
                        "total_members",
                        "total_messages",
                    )
                )

            data = paginate_data(forums, page_number, 10)
            return JsonResponse(
                data,
                safe=False,
            )
        except Forum.DoesNotExist:
            raise non_existing_data_exception("Forum")


class ApproveJoinForumRequest(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        request_id = self.kwargs["request_id"]

        try:
            forum_request = ForumRequest.objects.get(id=request_id)
            try:
                forum = Forum.objects.get(id=forum_request.forum_id)
                if forum.author == user:
                    try:
                        requester = User.objects.get(
                            user_key=forum_request.member.user_key
                        )
                        forum.forum_members.add(requester)
                        forum.total_members += 1
                        forum.updated_on = aware_datetime(datetime.now())
                        forum.save()
                        forum_request.is_approved = True
                        forum_request.is_declined = False
                        forum_request.updated_on = aware_datetime(datetime.now())
                        forum_request.save()
                        send_forum_join_request_approval_to_user(forum, requester)
                        return JsonResponse(
                            {
                                "status": "success",
                                "detail": "Successfully approved join forum request",
                            },
                            safe=False,
                        )
                    except User.DoesNotExist:
                        raise non_existing_data_exception("User")
                else:
                    raise cannot_perform_action(
                        "Unauthorized to approve this join request"
                    )
            except Forum.DoesNotExist:
                raise non_existing_data_exception("Forum")
        except ForumRequest.DoesNotExist:
            raise non_existing_data_exception("Forum request")


class DeclineJoinForumRequest(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        request_id = self.kwargs["request_id"]
        user = self.request.user

        try:
            forum_request = ForumRequest.objects.get(id=request_id)
            try:
                forum = Forum.objects.get(id=forum_request.forum_id)
                if forum.author == user:
                    try:
                        requester = User.objects.get(
                            user_key=forum_request.member.user_key
                        )
                        forum_request.is_approved = False
                        forum_request.is_declined = True
                        forum_request.save()
                        send_forum_join_request_decline_to_user(forum, requester)
                        return JsonResponse(
                            {
                                "status": "success",
                                "detail": "Successfully declined join forum request",
                            },
                            safe=False,
                        )
                    except User.DoesNotExist:
                        raise non_existing_data_exception("User")
                else:
                    raise cannot_perform_action(
                        "Unauthorized to decline this join request"
                    )
            except Forum.DoesNotExist:
                raise non_existing_data_exception("Forum")
        except ForumRequest.DoesNotExist:
            raise non_existing_data_exception("Forum request")


class GetForumJoinRequests(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        forum_id = self.kwargs["forum_id"]
        page_number = self.kwargs["page_number"]
        user = self.request.user

        try:
            forum = Forum.objects.get(id=forum_id)
            if user == forum.author:
                forum_request = list(
                    ForumRequest.objects.filter(
                        forum_id=forum_id, is_approved=False
                    ).values(
                        "id",
                        "forum__topic",
                        "member__first_name",
                        "member__last_name",
                        "member__email",
                        "created_on",
                    )
                )
                data = paginate_data(forum_request, page_number, 10)
                return JsonResponse(
                    data,
                    safe=False,
                )
            else:
                raise cannot_perform_action("Unauthorized to view forum requests")
        except Forum.DoesNotExist:
            raise non_existing_data_exception("Forum")


class ManageMyForum(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        forum_id = self.kwargs.get("forum_id")
        user = self.request.user

        try:
            forum = Forum.objects.get(id=forum_id)
            if not forum.author == user:
                raise cannot_perform_action("Unauthorized to manage forum")
            else:
                forum = (
                    Forum.objects.filter(id=forum_id)
                    .values(
                        "id",
                        "topic",
                        "description",
                        "tags",
                        "author__first_name",
                        "author__last_name",
                        "author__profile_image",
                        "author__is_verified",
                        "author__organization",
                        "approved_by__first_name",
                        "approved_by__last_name",
                        "approved_on",
                        "header_image",
                        "forum_members",
                        "total_likes",
                        "total_members",
                        "total_shares",
                        "is_approved",
                        "is_public",
                        "is_declined",
                        "created_on",
                    )
                    .first()
                )
                forum["virtual_meetings"] = list(
                    VirtualMeeting.objects.filter(forum_id=forum_id).values(
                        "id",
                        "meeting_agenda",
                        "meeting_url",
                        "scheduled_start_time",
                        "scheduled_end_time",
                        "organizer__first_name",
                        "organizer__last_name",
                        "total_attendees",
                    )
                )
                forum["media_files"] = list(
                    ForumFile.objects.filter(
                        forum_id=forum_id, file_category="Media Files"
                    ).values(
                        "id",
                        "description",
                        "file_name",
                        "file_category",
                        "file_type",
                        "file_url",
                        "file_key",
                        "created_on",
                    )
                )
                forum["files"] = list(
                    ForumFile.objects.filter(
                        forum_id=forum_id, file_category="Files"
                    ).values(
                        "id",
                        "description",
                        "file_name",
                        "file_category",
                        "file_type",
                        "file_url",
                        "file_key",
                        "created_on",
                    )
                )

                forum["chat_rooms"] = list(
                    ChatRoom.objects.filter(forum_id=forum_id).values(
                        "id",
                        "room_name",
                        "total_members",
                        "total_messages",
                    )
                )
                frm = Forum.objects.filter(id=forum_id).first()
                forum["members"] = list(
                    frm.forum_members.all().values(
                        "user_key", "first_name", "last_name"
                    )
                )

                return JsonResponse(
                    {
                        "status": "success",
                        "detail": "Forum deleted successfully",
                        "data": forum,
                    },
                    safe=False,
                )
        except Forum.DoesNotExist:
            raise non_existing_data_exception("Forum")
