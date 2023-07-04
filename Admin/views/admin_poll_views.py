import datetime

from django.db.models import Q
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from helpers.functions import aware_datetime
from helpers.status_codes import (action_authorization_exception,
                                  cannot_perform_action,
                                  duplicate_data_exception,
                                  non_existing_data_exception)
from helpers.validations import check_permission, check_required_fields, check_super_admin, unique_list
from Polls.models.poll_models import Poll, PollChoices, PollVote
from Polls.poll_helper import get_polls_by_logged_in_user, retrieve_poll_with_choices


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
            poll.is_approved = True
            poll.approved_by = user
            poll.updated_on = aware_datetime(datetime.datetime.now())
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