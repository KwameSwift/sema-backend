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
from helpers.validations import check_permission, check_required_fields
from Polls.models.poll_models import Poll, PollChoices, PollVotes
from Polls.poll_helper import retrieve_poll_with_choices


# Create a new Poll
class CreatePoll(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data
        user = self.request.user

        if not check_permission(user, "Polls", [2]):
            raise action_authorization_exception("Unauthorized to create blog post")

        check_required_fields(data, ["question", "choices", "start_date", "end_date"])

        try:
            Poll.objects.get(question=data["question"])
            raise duplicate_data_exception("Poll")
        except Poll.DoesNotExist:
            poll_details = {
                "question": data["question"],
                "author": user,
                "start_date": data["start_date"],
                "end_date": data["end_date"],
            }
            poll = Poll.objects.create(**poll_details)

            for choice in data["choices"]:
                PollChoices.objects.create(poll_id=poll.id, choice=choice)
            poll_data = (
                Poll.objects.filter(id=poll.id)
                .values(
                    "id",
                    "question",
                    "start_date",
                    "end_date",
                    "is_approved",
                    "is_ended",
                    "author__first_name",
                    "author__last_name",
                    "created_on",
                )
                .first()
            )
            poll_data["choices"] = list(
                PollChoices.objects.filter(poll_id=poll.id).values("id", "choice")
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
class VoteOnAPoll(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data
        user = self.request.user

        check_required_fields(data, ["poll_id", "choice_id"])

        try:
            poll = Poll.objects.get(id=data["poll_id"])
            if poll.is_ended:
                raise cannot_perform_action("Cannot vote. Poll has ended")

            exists = Poll.voters.through.objects.filter(
                Q(poll_id=poll.id) & Q(user_id=user.user_key)
            )
            if exists:
                return JsonResponse(
                    {
                        "status": "success",
                        "detail": "User already voted for this poll",
                    },
                    safe=False,
                )
            else:
                try:
                    poll_vote = PollVotes.objects.get(
                        poll=poll, poll_choice_id=data["choice_id"]
                    )
                    poll_vote.votes += 1
                    poll_vote.updated_on = aware_datetime(datetime.datetime.now())
                    poll_vote.save()
                except PollVotes.DoesNotExist:
                    poll_vote = PollVotes.objects.create(
                        poll_id=poll.id, poll_choice_id=data["choice_id"], votes=1
                    )
                poll.voters.add(user)
                poll.save()

                poll_stats = retrieve_poll_with_choices(poll.id)

                return JsonResponse(
                    {
                        "status": "success",
                        "detail": "Vote has been cast",
                        "data": poll_stats,
                    },
                    safe=False,
                )
        except Poll.DoesNotExist:
            raise non_existing_data_exception("Poll")


# Get All Polls and their results
class GetAllPollResults(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if not check_permission(user, "Polls", [2]):
            raise action_authorization_exception("Unauthorized to view poll results")

        Poll.objects.filter(end_date__lt=datetime.datetime.now()).update(is_ended=True)

        polls = Poll.objects.all().values("id")

        for poll in polls:
            poll_stats = retrieve_poll_with_choices(poll["id"])
            poll["stats"] = poll_stats

        return JsonResponse(
            {"status": "success", "detail": "Vote has been cast", "data": list(polls)},
            safe=False,
        )


# Get All Polls and their results
class GetAllApprovedPolls(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        Poll.objects.filter(
            end_date__lt=aware_datetime(datetime.datetime.now())
        ).update(is_ended=True)

        polls = Poll.objects.filter(is_approved=True).values(
            "id",
            "question",
            "start_date",
            "end_date",
            "is_approved",
            "is_ended",
            "author__first_name",
            "author__last_name",
            "created_on",
        )

        for poll in polls:
            if poll["is_ended"]:
                poll["stats"] = retrieve_poll_with_choices(poll["id"], type="All")

        return JsonResponse(
            {
                "status": "success",
                "detail": "Polls retrieved successfully",
                "data": list(polls),
            },
            safe=False,
        )


# Get All Polls and their results
class GetMyPolls(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if not check_permission(user, "Polls", [1, 2]):
            raise action_authorization_exception("Unauthorized to view poll results")

        Poll.objects.filter(end_date__lt=datetime.datetime.now()).update(is_ended=True)

        polls = Poll.objects.filter(author=user).values(
            "id",
            "question",
            "start_date",
            "end_date",
            "is_approved",
            "is_ended",
            "author__first_name",
            "author__last_name",
            "created_on",
        )

        for poll in polls:
            poll_stats = retrieve_poll_with_choices(poll["id"])
            poll["stats"] = poll_stats

        return JsonResponse(
            {
                "status": "success",
                "detail": "Polls retrieved successfully",
                "data": list(polls),
            },
            safe=False,
        )
