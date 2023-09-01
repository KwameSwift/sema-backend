import json

from django.db.models import Q
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Forum.forum_helper import (
    send_forum_join_request_to_admin,
    send_forum_request_response_to_user,
)
from Forum.models import (
    Forum,
    ForumFile,
    VirtualMeeting,
    ChatRoom,
    ForumRequest,
)
from helpers.azure_file_handling import (
    delete_blob,
    create_forum_header,
)
from helpers.functions import paginate_data
from helpers.status_codes import (
    action_authorization_exception,
    duplicate_data_exception,
    non_existing_data_exception,
    cannot_perform_action,
)
from helpers.validations import check_permission, check_required_fields


# Create a Forum
class CreateForum(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data
        user = self.request.user
        file = request.FILES.get("file")

        if not check_permission(user, "Forums", [2]):
            raise action_authorization_exception("Unauthorized to create forums")

        if file:
            file = data.pop("file", None)

        data = json.dumps(data)
        data = json.loads(data)

        check_required_fields(data, ["topic", "description", "tags[]"])
        data["tags"] = eval(data["tags[]"])
        data.pop("tags[]", None)
        data["author"] = user

        try:
            Forum.objects.get(topic=data["topic"], author=user)
            raise duplicate_data_exception("Forum")
        except Forum.DoesNotExist:
            forum = Forum.objects.create(**data)
            if file:
                header_image = create_forum_header(file, forum, user)
                Forum.objects.filter(id=forum.id).update(
                    header_key=header_image["file_key"],
                    header_image=header_image["file_url"],
                )
            forum = Forum.objects.get(id=forum.id)
            forum.forum_members.add(user)
            forum.total_members += 1
            forum.save()
            data = {
                "id": forum.id,
                "topic": forum.topic,
                "description": forum.description,
            }
            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Forum created successfully",
                    "data": data,
                },
                safe=False,
            )


class DeleteForum(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        forum_id = self.kwargs.get("forum_id")

        if not check_permission(user, "Forums", [2]):
            raise action_authorization_exception("Unauthorized to create forums")
        try:
            forum = Forum.objects.get(id=forum_id)
            if user.role.name == "Super Admin" or forum.author == user:
                forum_files = ForumFile.objects.filter(forum_id=forum.id).values(
                    "file_key"
                )
                container = (
                    f"{forum.author.first_name}-{forum.author.last_name}".lower()
                )
                for file in forum_files:
                    delete_blob(container, file["file_key"])
                delete_blob(container, forum.header_key)
                forum.delete()
                return JsonResponse(
                    {"status": "success", "detail": "Forum deleted successfully"},
                    safe=False,
                )
            else:
                raise cannot_perform_action("Cannot delete forum")
        except Forum.DoesNotExist:
            non_existing_data_exception("Forum")


class GetSingleForum(APIView):
    def get(self, request, *args, **kwargs):
        forum_id = self.kwargs.get("forum_id")
        user = self.request.user

        try:
            Forum.objects.get(id=forum_id)

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
            forum["files"] = list(
                ForumFile.objects.filter(forum_id=forum_id).values(
                    "id", "description", "file_type", "file_url", "created_on"
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

            if user.is_authenticated:
                liked = Forum.forum_likers.through.objects.filter(
                    Q(forum_id=forum_id) & Q(user_id=user.user_key)
                )
                member = Forum.forum_members.through.objects.filter(
                    Q(forum_id=forum_id) & Q(user_id=user.user_key)
                )
                forum["has_liked"] = True if liked else False
                forum["is_member"] = True if member else False
                forum["is_authenticated"] = True
            else:
                forum["is_authenticated"] = False

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


class GetAllForums(APIView):
    def get(self, request, *args, **kwargs):
        page_number = self.kwargs.get("page_number")
        user = self.request.user
        try:
            forums = Forum.objects.filter(is_approved=True, is_declined=False).values(
                "id",
                "topic",
                "description",
                "tags",
                "author_id",
                "author__first_name",
                "author__last_name",
                "author__profile_image",
                "author__is_verified",
                "author__organization",
                "approved_by__first_name",
                "approved_by__last_name",
                "approved_on",
                "total_likes",
                "total_shares",
                "is_approved",
                "is_public",
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

                if user.is_authenticated:
                    forum["is_owner"] = (
                        True if forum["author_id"] == user.user_key else False
                    )
                    liked = Forum.forum_likers.through.objects.filter(
                        Q(forum_id=forum["id"]) & Q(user_id=user.user_key)
                    )
                    member = Forum.forum_members.through.objects.filter(
                        Q(forum_id=forum["id"]) & Q(user_id=user.user_key)
                    )
                    forum["has_liked"] = True if liked else False
                    forum["is_member"] = True if member else False
                    forum["is_authenticated"] = True
                else:
                    forum["is_owner"] = False
                    forum["is_authenticated"] = False
                    forum["is_member"] = False
                    forum["has_liked"] = False
                forum.pop("author_id", None)
            data = paginate_data(forums, page_number, 10)
            return JsonResponse(
                data,
                safe=False,
            )
        except Forum.DoesNotExist:
            raise non_existing_data_exception("Forum")


class LikeAForum(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        forum_id = self.kwargs["forum_id"]

        try:
            forum = Forum.objects.get(id=forum_id)
            exists = Forum.forum_likers.through.objects.filter(
                Q(forum_id=forum_id) & Q(user_id=user.user_key)
            )
            if exists:
                likes = forum.total_likes - 1
                forum.forum_likers.remove(user)
                message = "Forum unliked"
            else:
                forum.forum_likers.add(user)
                likes = forum.total_likes + 1
                message = "Forum liked"

            forum.total_likes = likes
            forum.save()

            liked_forums = user.forum_likers.all()
            forum_ids = [forum.id for forum in liked_forums]

            return JsonResponse(
                {
                    "status": "success",
                    "detail": message,
                    "total_likes": likes,
                    "liked_forums": forum_ids,
                },
                safe=False,
            )
        except Forum.DoesNotExist:
            raise non_existing_data_exception("Forum")


class JoinForum(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        forum_id = self.kwargs["forum_id"]
        user = self.request.user

        try:
            forum = Forum.objects.get(id=forum_id)

            exists = Forum.forum_members.through.objects.filter(
                Q(forum_id=forum) & Q(user_id=user.user_key)
            )
            if forum.is_public:
                if exists:
                    raise cannot_perform_action("User already a member of forum")
                else:
                    forum.forum_members.add(user)
                    forum.total_members += 1
                    forum.save()
                    message = "User successfully joined forum"
            else:
                send_forum_join_request_to_admin(forum, forum.author.email, user)
                send_forum_request_response_to_user(forum, user)
                try:
                    ForumRequest.objects.get(forum=forum, member=user)
                except ForumRequest.DoesNotExist:
                    ForumRequest.objects.create(forum=forum, member=user)
                message = "Join request sent to Forum Admin"
            return JsonResponse(
                {"status": "success", "detail": message},
                safe=False,
            )
        except Forum.DoesNotExist:
            raise non_existing_data_exception("Forum")


class LeaveForum(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        forum_id = self.kwargs["forum_id"]
        user = self.request.user

        try:
            forum = Forum.objects.get(id=forum_id)
            exists = Forum.forum_members.through.objects.filter(
                Q(forum_id=forum) & Q(user_id=user.user_key)
            )
            if exists:
                forum.forum_members.remove(user)
                forum.total_members -= 1
                forum.save()
                return JsonResponse(
                    {"status": "success", "detail": "User left forum"},
                    safe=False,
                )
            else:
                raise cannot_perform_action("User not a member of forum")
        except Forum.DoesNotExist:
            raise non_existing_data_exception("Forum")


class UpdateForum(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        forum_id = self.kwargs["forum_id"]
        data = request.data
        user = self.request.user
        file = request.FILES.get("file")

        if not check_permission(user, "Forums", [2]):
            raise action_authorization_exception("Unauthorized to update forum")

        try:
            forum = Forum.objects.get(id=forum_id)
            container_name = (
                f"{forum.author.first_name}-{forum.author.last_name}".lower()
            )

            if forum.author_id != user.user_key:
                raise action_authorization_exception("Cannot update this forum")

            if file:
                file = data.pop("file", None)
                delete_blob(container_name, forum.header_key)
                header_image = create_forum_header(file, forum, user)
                forum.header_key = header_image["file_key"]
                forum.header_image = header_image["file_url"]
                forum.save()

            forum.refresh_from_db()
            data = json.dumps(data)
            data = json.loads(data)

            if "tags[]" in data:
                data["tags"] = eval(data["tags[]"])
                data.pop("tags[]", None)
            Forum.objects.filter(id=forum_id).update(**data)

            return JsonResponse(
                {"status": "success", "detail": "Forum updated successfully"},
                safe=False,
            )
        except Forum.DoesNotExist:
            raise non_existing_data_exception("Forum")


class SearchForum(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        page_number = self.kwargs["page_number"]
        search_query = request.data.get("search_query")

        if user.role.name == "Super Admin":
            forums = Forum.objects.filter(
                Q(tags__icontains=search_query)
                | Q(topic__icontains=search_query)
                | Q(description__icontains=search_query)
            ).values(
                "id",
                "topic",
                "description",
                "tags",
                "author",
                "author__first_name",
                "author__last_name",
                "author__profile_image",
                "author__is_verified",
                "author__organization",
                "approved_by__first_name",
                "approved_by__last_name",
                "approved_on",
                "total_likes",
                "total_shares",
                "is_public",
                "is_approved",
                "is_declined",
                "created_on",
            )
            for forum in forums:
                forum["is_owner"] = True if forum["author"] == user.user_key else False
                forum.pop("author", None)
        else:
            forums = Forum.objects.filter(
                Q(author=user),
                Q(tags__icontains=search_query)
                | Q(topic__icontains=search_query)
                | Q(description__icontains=search_query),
            ).values(
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
                "total_likes",
                "total_shares",
                "is_public",
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
