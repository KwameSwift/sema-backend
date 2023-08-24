import json
from datetime import datetime

from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Forum.models import ChatRoom, UserChatRoom, Forum
from chat_channels.sender_functions import send_group_message
from helpers.azure_file_handling import create_chat_shared_file
from helpers.status_codes import (
    action_authorization_exception,
    duplicate_data_exception,
    cannot_perform_action,
    non_existing_data_exception,
)
from helpers.validations import check_permission, check_required_fields


class CreateChatRooms(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data
        user = self.request.user
        forum_id = self.kwargs.get("forum_id")

        if not check_permission(user, "Forums", [2]):
            raise action_authorization_exception("Unauthorized to create chat room")

        check_required_fields(data, ["room_name", "description"])

        try:
            ChatRoom.objects.get(room_name=data["room_name"], creator=user)
            raise duplicate_data_exception("Meeting Room")
        except ChatRoom.DoesNotExist:
            try:
                forum = Forum.objects.get(id=forum_id)
                chat_room = ChatRoom.objects.create(
                    forum=forum,
                    room_name=data["room_name"],
                    description=data["description"],
                    creator=user,
                    total_members=1,
                )

                UserChatRoom.objects.create(
                    chat_room_id=chat_room.id,
                    member=user,
                    membership_type="Owner",
                )
                data = {
                    "id": chat_room.id,
                    "room_name": chat_room.room_name,
                    "description": chat_room.description,
                }

                return JsonResponse(
                    {
                        "status": "success",
                        "detail": "Meeting Room created successfully",
                        "data": data,
                    },
                    safe=False,
                )
            except Forum.DoesNotExist:
                raise non_existing_data_exception("Forum")


class DeleteChatRoom(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        room_id = self.kwargs["room_id"]

        try:
            meeting_room = ChatRoom.objects.get(id=room_id)
            if (
                user.user_key == meeting_room.creator_id
                or user.role.name == "Super Admin"
            ):
                meeting_room.delete()
                return JsonResponse(
                    {
                        "status": "success",
                        "detail": "Chat room deleted successfully",
                    },
                    safe=False,
                )
            else:
                raise cannot_perform_action("Cannot delete this chat room")

        except ChatRoom.DoesNotExist:
            raise non_existing_data_exception("Chat Room")


class GetChatRoom(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        room_id = self.kwargs["room_id"]

        try:
            chat_room = ChatRoom.objects.filter(id=room_id).values(
                "id",
                "room_name",
                "description",
                "creator_id",
                "creator__first_name",
                "creator__last_name",
                "total_members",
                "total_messages",
                "creator__is_verified",
                "creator__profile_image",
                "created_on",
            )

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Meeting Room retrieved successfully",
                    "data": chat_room[0],
                },
                safe=False,
            )
        except IndexError:
            raise non_existing_data_exception("Chat Room")


class UpdateChatRoom(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data
        room_id = self.kwargs["room_id"]

        if not check_permission(user, "Forums", [2]):
            raise action_authorization_exception("Unauthorized to create meeting room")

        try:
            ChatRoom.objects.get(id=room_id)
            ChatRoom.objects.filter(id=room_id).update(**data)

            return JsonResponse(
                {"status": "success", "detail": "Meeting Room updated successfully"},
                safe=False,
            )
        except ChatRoom.DoesNotExist:
            raise non_existing_data_exception("Meeting Room")


class JoinChatRoom(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        room_id = self.kwargs["room_id"]
        user = self.request.user

        try:
            chat_room = ChatRoom.objects.get(id=room_id)
            try:
                UserChatRoom.objects.get(meeting_room_id=chat_room.id, member=user)
                cannot_perform_action("User already part of chat room")
            except UserChatRoom.DoesNotExist:
                UserChatRoom.objects.create(
                    meeting_room_id=chat_room.id,
                    member=user,
                    membership_type="Member",
                )
                chat_room.total_members += 1
                chat_room.save()
                return JsonResponse(
                    {"status": "success", "detail": "User joined chat room"},
                    safe=False,
                )
        except ChatRoom.DoesNotExist:
            raise non_existing_data_exception("Chat Room")


class LeaveChatRoom(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        room_id = self.kwargs["room_id"]
        user = self.request.user

        try:
            chat_room = ChatRoom.objects.get(id=room_id)
            try:
                user_chat_room = UserChatRoom.objects.get(
                    meeting_room_id=chat_room.id, member=user
                )
                user_chat_room.delete()

                chat_room.total_members -= 1
                chat_room.save()
                return JsonResponse(
                    {"status": "success", "detail": "User left chat room"},
                    safe=False,
                )
            except UserChatRoom.DoesNotExist:
                cannot_perform_action("User not part of chat room")
        except ChatRoom.DoesNotExist:
            raise non_existing_data_exception("Chat Room")


class SendMessageToChatRoom(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data
        room_id = self.kwargs["room_id"]
        user = self.request.user
        message = request.data.get("message")
        files = request.FILES.getlist("files[]")

        if files:
            files = data.pop("files[]", None)

        data = json.dumps(data)
        data = json.loads(data)
        try:
            chat_room = ChatRoom.objects.get(id=room_id)
            try:
                UserChatRoom.objects.get(chat_room_id=room_id, member=user)
                data = {
                    "chat_room_id": chat_room.id,
                    "sender": f"{user.first_name} {user.last_name}",
                    "timestamp": datetime.now().isoformat(),
                }
                if files:
                    check_required_fields(data, ["description"])
                    urls = create_chat_shared_file(
                        files, chat_room, user, data["description"]
                    )
                    data["description"] = data.get("description")
                    data["files"] = urls
                else:
                    data["message"] = message
                room_name = str(chat_room.room_name).lower().replace(" ", "_")
                send_group_message(room_name, data)
                chat_room.total_messages += 1
                chat_room.save()
                return JsonResponse(
                    {"status": "success", "detail": "Message sent", "data": data},
                    safe=False,
                )
            except UserChatRoom.DoesNotExist:
                raise cannot_perform_action("User not part of chat room")
        except ChatRoom.DoesNotExist:
            raise non_existing_data_exception("Chat room")
