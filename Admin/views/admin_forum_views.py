from datetime import datetime

from django.db.models import Q
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Forum.forum_helper import send_forum_declination_mail
from Forum.models import Forum, ForumFile, VirtualMeeting, ChatRoom, ForumDiscussion
from helpers.functions import paginate_data, aware_datetime
from helpers.status_codes import (
    action_authorization_exception,
    cannot_perform_action,
    non_existing_data_exception,
)
from helpers.validations import check_permission, check_required_fields


class ApproveForum(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        forum_id = self.kwargs.get("forum_id")
        status = self.kwargs.get("status")

        if not check_permission(user, "Forums", [2]):
            raise action_authorization_exception(
                "Unauthorized to approve or disapprove forums"
            )
        try:
            forum = Forum.objects.get(id=forum_id)
            if user.role.name == "Super Admin":
                if status == 1:
                    forum.is_approved = True
                    forum.approved_by = user
                    forum.approved_on = aware_datetime(datetime.now())
                    message = "Forum approved successfully"
                else:
                    forum.is_approved = False
                    forum.approved_by = None
                    forum.approved_on = None
                    message = "Forum disapproved successfully"

                forum.updated_on = aware_datetime(datetime.now())
                forum.save()
                return JsonResponse(
                    {"status": "success", "detail": message},
                    safe=False,
                )
            else:
                raise cannot_perform_action("Cannot approve forum")
        except Forum.DoesNotExist:
            non_existing_data_exception("Forum")


class DeclineForum(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        forum_id = self.kwargs.get("forum_id")
        data = request.data

        if not check_permission(user, "Forums", [2]):
            raise action_authorization_exception("Unauthorized to decline forums")
        try:
            forum = Forum.objects.get(id=forum_id)
            if user.role.name == "Super Admin":
                check_required_fields(data, ["comment", "description", "tags[]"])
                forum.is_declined = True
                forum.is_approved = False
                forum.decline_comment = data["comment"]
                forum.save()
                send_forum_declination_mail(forum, data["comment"])
                return JsonResponse(
                    {"status": "success", "detail": "Forum declined successfully"},
                    safe=False,
                )
            else:
                raise cannot_perform_action("Cannot decline forum")
        except Forum.DoesNotExist:
            non_existing_data_exception("Forum")


class AdminGetAllForums(APIView):
    def get(self, request, *args, **kwargs):
        page_number = self.kwargs.get("page_number")
        data_type = self.kwargs["data_type"]
        user = self.request.user

        query = Q()
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
                "total_comments",
                "total_shares",
                "is_approved",
                "is_public",
                "is_declined",
                "created_on",
            )
            for forum in forums:
                forum["is_owner"] = True if forum["author"] == user.user_key else False
                forum.pop("author", None)
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
                forum["discussions"] = list(
                    ForumDiscussion.objects.filter(forum_id=forum["id"]).values(
                        "id",
                        "comment",
                        "commentor__first_name",
                        "commentor__last_name",
                        "commentor__profile_image",
                        "is_forum_admin",
                        "total_likes",
                        "created_on",
                    )
                )

            data = paginate_data(forums, page_number, 10)
            return JsonResponse(
                data,
                safe=False,
            )
        except Forum.DoesNotExist:
            raise non_existing_data_exception("Forum")
