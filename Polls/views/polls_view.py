from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from helpers.functions import paginate_data
from helpers.status_codes import (action_authorization_exception,
                                  duplicate_data_exception,
                                  non_existing_data_exception)
from helpers.validations import check_permission, check_required_fields
from Polls.models.poll_models import Poll, PollChoices


# Create a new Poll
class CreatePoll(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data
        user = self.request.user

        if not check_permission(user, "Polls", [2]):
            raise action_authorization_exception("Unauthorized to create blog post")

        check_required_fields(data, ["question", "choices"])

        try:
            Poll.objects.get(question=data["question"])
            raise duplicate_data_exception("Poll")
        except Poll.DoesNotExist:
            poll_details = {"question": data["question"], "author": user}
            poll = Poll.objects.create(**poll_details)

            for choice in data["choices"]:
                PollChoices.objects.create(poll_id=poll.id, choice=choice)
            poll_data = (
                Poll.objects.filter(id=poll.id)
                .values(
                    "id",
                    "question",
                    "author__first_name",
                    "author__last_name",
                    "created_on",
                )
                .first()
            )
            poll_data["choices"] = list(
                PollChoices.objects.filter(poll_id=poll.id).values(
                    "id", "choice", "votes"
                )
            )
            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Poll created and submitted for review",
                    "data": poll_data,
                },
                safe=False,
            )
            
            
# Cast a vote on a poll
# class VoteOnAPoll(APIView):
    
