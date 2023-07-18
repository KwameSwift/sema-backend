import datetime

from django.db.models import Q
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Polls.models.poll_models import Poll
from Polls.poll_helper import (retrieve_poll_with_choices)
from Utilities.models.documents_model import UserDocuments
from helpers.functions import aware_datetime, paginate_data
from helpers.status_codes import (action_authorization_exception,
                                  non_existing_data_exception)
from helpers.validations import (check_permission, check_super_admin)


class ApprovePoll(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        poll_id = self.kwargs.get("poll_id")

        if not check_super_admin(user):
            raise action_authorization_exception("Unauthorized to approve Poll")

        try:
            poll = Poll.objects.get(id=poll_id)
            poll.is_approved = True if poll.is_approved else False
            poll.approved_on = aware_datetime(datetime.datetime.now())
            poll.updated_on = aware_datetime(datetime.datetime.now())
            poll.save()
            poll.refresh_from_db()
            
            poll.approved_by = user if poll.is_approved else None
            poll.save()

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Poll approved and published successfully",
                },
                safe=False,
            )
        except Poll.DoesNotExist:
            raise non_existing_data_exception("Poll")


class AdminViewSinglePoll(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        poll_id = self.kwargs.get("poll_id")

        if not check_super_admin(user):
            raise action_authorization_exception("Unauthorized to approve Poll")

        try:
            poll = Poll.objects.get(id=poll_id)
            poll_data = retrieve_poll_with_choices(poll.id)

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


# Get All Polls and their results
class AdminGetAllPolls(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        data_type = self.kwargs["data_type"]
        page_number = self.kwargs["page_number"]
        user = self.request.user

        if not check_permission(user, "Polls", [1, 2]):
            raise action_authorization_exception("Unauthorized to view poll results")

        Poll.objects.filter(
            end_date__lt=aware_datetime(datetime.datetime.now())
        ).update(is_ended=True)
        query = Q()
        if data_type == 1:
            query &= Q(is_approved=True)
        elif data_type == 2:
            query &= Q(is_approved=False)

        polls = Poll.objects.filter(query).values(
            "id",
            "question",
            "snapshot_location",
            "start_date",
            "end_date",
            "is_approved",
            "author_id",
            "author__first_name",
            "author__last_name",
            "author__is_verified",
            "author__profile_image",
            "approved_by__first_name",
            "approved_by__last_name",
            "approved_on",
            "created_on",
        )

        for poll in polls:
            image = (
                UserDocuments.objects.filter(
                    owner_id=poll["author_id"], document_type="Profile Image"
                )
                .values("document_location")
                .first()
            )
        data = paginate_data(polls, page_number, 10)
        return JsonResponse(
            data,
            safe=False,
        )
