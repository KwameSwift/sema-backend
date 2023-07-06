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
from helpers.validations import check_permission, check_required_fields, unique_list
from Polls.models.poll_models import Poll, PollChoices, PollVote
from Polls.poll_helper import get_polls_by_logged_in_user, retrieve_poll_with_choices


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
            start_date = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d")
            end_date = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d")
            poll_details = {
                "question": data["question"],
                "author": user,
                "start_date": aware_datetime(start_date),
                "end_date": aware_datetime(end_date)
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

        check_required_fields(data, ["poll_id", "choice"])

        try:
            poll = Poll.objects.get(id=data["poll_id"])
            if poll.is_ended:
                raise cannot_perform_action("Cannot vote. Poll has ended")

            try:
                PollVote.objects.get(poll=poll, voter=user)
                raise cannot_perform_action("User already voted for this poll")
            except PollVote.DoesNotExist:
                try:
                    poll_choice = PollChoices.objects.get(
                        poll=poll, choice=data["choice"]
                    )
                    poll_choice.votes += 1
                    poll_choice.updated_on = aware_datetime(datetime.datetime.now())
                    poll_choice.save()
                    
                    PollVote.objects.create(
                        poll=poll, voter=user, poll_choice=poll_choice
                    )
                except PollChoices.DoesNotExist:
                    raise non_existing_data_exception("Poll Choice")

                # poll_choice = get_polls_by_logged_in_user(user)
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

        Poll.objects.filter(end_date__lt=aware_datetime(datetime.datetime.now())).update(is_ended=True)

        polls = Poll.objects.all().values("id")

        for poll in polls:
            poll_stats = retrieve_poll_with_choices(poll["id"])
            poll["stats"] = poll_stats

        return JsonResponse(
            {"status": "success", "detail": "Vote has been cast", "data": list(polls)},
            safe=False,
        )


# Get All Polls and their results
class GetAllApprovedPollsByUser(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        
        data = []
        Poll.objects.filter(
            end_date__lt=aware_datetime(datetime.datetime.now())
        ).update(is_ended=True)

        polls = Poll.objects.filter(is_approved=True).values(
            "id",
            "title",
            "description",
            "question",
            "start_date",
            "end_date",
            "is_approved",
            "is_ended",
            "author__first_name",
            "author__last_name",
            "created_on",
        )

        poll_data = get_polls_by_logged_in_user(user)
        for item in poll_data:
            if item["is_ended"] and not PollVote.objects.filter(voter=user, poll_id=item["id"]).exists():
                item = retrieve_poll_with_choices(item["id"])
            data.append(item) 
                
        return JsonResponse(
            {
                "status": "success",
                "detail": "Polls retrieved successfully",
                "data": data,
            },
            safe=False,
        )
        
        
# Get All Polls and their results
class GetAllApprovedPolls(APIView):

    def get(self, request, *args, **kwargs):
        Poll.objects.filter(
            end_date__lt=aware_datetime(datetime.datetime.now())
        ).update(is_ended=True)

        polls = Poll.objects.filter(is_approved=True).values(
            "id",
            "title",
            "description",
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
                
            else:
               poll["choices"] = list(
                PollChoices.objects.filter(poll_id=poll["id"]).values("id", "choice")
            )
            
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
        data_type = self.kwargs["data_type"]
        user = self.request.user

        if not check_permission(user, "Polls", [1, 2]):
            raise action_authorization_exception("Unauthorized to view poll results")

        Poll.objects.filter(end_date__lt=aware_datetime(datetime.datetime.now())).update(is_ended=True)
        query = Q(author=user)
        if data_type == 1:
            query &= Q(is_approved=True)
        elif data_type == 2:
            query &= Q(is_approved=False)
            
        polls = Poll.objects.filter(query).values(
            "id",
            "title",
            "description",
            "question",
            "start_date",
            "end_date",
            "is_approved",
            "is_ended",
            "created_on",
        )

        # for poll in polls:
        #     poll["stats"] = retrieve_poll_with_choices(poll["id"], type="All")

        return JsonResponse(
            {
                "status": "success",
                "detail": "Polls retrieved successfully",
                "data": list(polls),
            },
            safe=False,
        )
