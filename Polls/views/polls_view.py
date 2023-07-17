import datetime
import json
import os

from django.db.models import Q, Sum
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Polls.models.poll_models import Poll, PollChoices, PollVote
from Polls.poll_helper import (get_polls_by_logged_in_user,
                               retrieve_poll_with_choices)
from Utilities.models.documents_model import UserDocuments
from helpers.azure_file_handling import delete_blob, upload_poll_file_or_pdf_to_azure, upload_cover_image
from helpers.functions import aware_datetime, paginate_data
from helpers.status_codes import (action_authorization_exception,
                                  cannot_perform_action,
                                  duplicate_data_exception,
                                  non_existing_data_exception)
from helpers.validations import (check_permission, check_required_fields)

LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")


# Create a new Poll
class CreatePoll(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data
        user = self.request.user
        files = request.FILES.get("files")

        if files:
            files = data.pop("files", None)

        data = json.dumps(data)
        data = json.loads(data)

        if not check_permission(user, "Polls", [2]):
            raise action_authorization_exception("Unauthorized to create blog post")

        check_required_fields(data, ["question", "choices", "start_date", "end_date"])

        try:
            Poll.objects.get(question=data["question"])
            raise duplicate_data_exception("Poll")
        except Poll.DoesNotExist:
            data["start_date"] = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d").date()
            data["end_date"] = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d").date()
            data["author_id"] = user.user_key
            choices = data.pop("choices", None)
            poll = Poll.objects.create(**data)

            if files:
                for file in files:
                    res_data = upload_poll_file_or_pdf_to_azure(file, user, poll)
                    if type(res_data) is tuple:
                        upload_cover_image(request, res_data, poll=poll)

            new_choices = eval(choices)
            for choice in new_choices:
                PollChoices.objects.create(poll_id=poll.id, choice=choice)
            poll_data = (
                Poll.objects.filter(id=poll.id)
                .values(
                    "id",
                    "question",
                    "start_date",
                    "file_location",
                    "snapshot_location",
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

        check_required_fields(data, ["poll_id", "choice_id", "comments"])

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
                        poll=poll, id=data["choice_id"]
                    )
                    poll_choice.votes += 1
                    poll_choice.updated_on = aware_datetime(datetime.datetime.now())
                    poll_choice.save()

                    PollVote.objects.create(
                        poll=poll, voter=user, poll_choice=poll_choice, comments=data["comments"]
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

        Poll.objects.filter(
            end_date__lt=aware_datetime(datetime.datetime.now())
        ).update(is_ended=True)

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

        poll_data = get_polls_by_logged_in_user(user)
        for item in poll_data:
            if (
                    item["is_ended"]
                    and not PollVote.objects.filter(voter=user, poll_id=item["id"]).exists()
            ):
                item = retrieve_poll_with_choices(item["id"])

            image = (
                UserDocuments.objects.filter(
                    owner_id=item["author_id"], document_type="Profile Image"
                )
                .values("document_location")
                .first()
            )
            item["total_votes"] = PollChoices.objects.filter(poll_id=item["id"]).aggregate(total_votes=Sum('votes'))[
                'total_votes']
            item["author_profile_image"] = image["document_location"] if image else None
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
        page_number = self.kwargs.get('page_number')
        Poll.objects.filter(
            end_date__lt=aware_datetime(datetime.datetime.now()), is_ended=False
        ).update(is_ended=True)

        polls = Poll.objects.filter(is_approved=True).values(
            "id",
            "title",
            "file_location",
            "snapshot_location",
            "start_date",
            "end_date",
            "is_approved",
            "is_ended",
            "author_id",
            "author__first_name",
            "author__last_name",
            "author__is_verified",
            "approved_on",
            "created_on",
        )

        for poll in polls:
            poll["total_votes"] = PollChoices.objects.filter(poll_id=poll["id"]).aggregate(total_votes=Sum('votes'))[
                'total_votes']
            image = (
                UserDocuments.objects.filter(
                    owner_id=poll["author_id"], document_type="Profile Image"
                )
                .values("document_location")
                .first()
            )
            poll["author_profile_image"] = image["document_location"] if image else None
            if poll["is_ended"]:
                poll["stats"] = retrieve_poll_with_choices(poll["id"], type="All")

            else:
                poll["choices"] = list(
                    PollChoices.objects.filter(poll_id=poll["id"]).values(
                        "id", "choice"
                    )
                )
        data = paginate_data(polls, page_number, 10)
        return JsonResponse(
            data,
            safe=False,
        )


# Get All Polls and their results
class GetMyPolls(APIView):
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
        query = Q(author=user)
        if data_type == 1:
            query &= Q(is_approved=True)
        elif data_type == 2:
            query &= Q(is_approved=False)

        polls = Poll.objects.filter(query).values(
            "id",
            "questiion",
            "file_location",
            "snapshot_location",
            "start_date",
            "end_date",
            "is_approved",
            "approved_on",
            "created_on",
        )

        # for poll in polls:
        #     poll["stats"] = retrieve_poll_with_choices(poll["id"], type="All")
        data = paginate_data(polls, page_number, 10)
        return JsonResponse(
            data,
            safe=False
        )


class UpdatePoll(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        poll_id = self.kwargs["poll_id"]
        files = request.FILES.get("files")
        user = self.request.user
        data = request.data

        if not check_permission(user, "Polls", [2]):
            raise action_authorization_exception("Unauthorized to view poll results")

        try:
            poll = Poll.objects.get(id=poll_id)
            container_name = f"{poll.author.first_name}-{poll.author.last_name}".lower()

            if files:
                files = data.pop("files", None)
                delete_blob(container_name, poll.file_key)
                delete_blob(container_name, poll.snapshot_key)
                poll.file_key = None
                poll.file_location = None
                poll.snapshot_key = None
                poll.snapshot_location = None
                poll.save()
                for file in files:
                    res_data = upload_poll_file_or_pdf_to_azure(file, user, poll)

                    if type(res_data) is tuple:
                        upload_cover_image(request, res_data, poll=poll)

            data = json.dumps(data)
            data = json.loads(data)
            poll.refresh_from_db()
            if "choices" in data:
                new_choices = eval(data["choices"])
                PollChoices.objects.filter(poll_id=poll_id).delete()
                for choice in new_choices:
                    PollChoices.objects.create(poll_id=poll_id, choice=choice)
                data.pop("choices", None)

            if "is_document_deleted" in data and data["is_document_deleted"]:
                delete_blob(container_name, poll.file_key)
                poll.file_key = None
                poll.file_location = None
                poll.save()
                data.pop("is_document_deleted", None)

            if "start_date" in data:
                data["start_date"] = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d").date()
            if "end_date" in data:
                data["end_date"] = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d").date()
                if data["end_date"] >= datetime.datetime.now().date():
                    data["is_ended"] = False

            data["updated_on"] = aware_datetime(datetime.datetime.now())
            Poll.objects.filter(id=poll_id).update(**data)
            return JsonResponse(
                {"status": "success", "detail": "Poll updated successfully"},
                safe=False,
            )
        except Poll.DoesNotExist:
            raise non_existing_data_exception("Poll")


class DeletePoll(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        poll_id = self.kwargs["poll_id"]
        user = self.request.user

        if not check_permission(user, "Polls", [2]):
            raise action_authorization_exception("Unauthorized to view poll results")

        try:
            poll = Poll.objects.get(id=poll_id)
            container_name = f"{poll.author.first_name}-{poll.author.last_name}".lower()
            delete_blob(container_name, poll.file_key)
            delete_blob(container_name, poll.snapshot_key)
            PollChoices.objects.filter(poll_id=poll_id).delete()
            PollVote.objects.filter(poll_id=poll_id).delete()
            poll.delete()

            return JsonResponse(
                {"status": "success", "detail": "Poll deleted successfully"},
                safe=False,
            )
        except Poll.DoesNotExist:
            raise non_existing_data_exception("Poll")


class SearchPolls(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        page_number = self.kwargs.get("page_number")
        user = self.request.user
        data = request.data

        if not check_permission(user, "Polls", [1, 2]):
            raise action_authorization_exception("Unauthorized to view poll results")

        check_required_fields(data, ["search_query"])

        polls = Poll.objects.filter(
            Q(description__icontains=data["search_query"])
            | Q(question__icontains=data["search_query"])
            | Q(author__first_name__icontains=data["search_query"])
            | Q(author__last_name__icontains=data["search_query"])
        )

        if not user.is_admin:
            polls = polls.filter(Q(author=user))

        polls = polls.values(
            "id",
            "description",
            "file_location",
            "snapshot_location",
            "end_date",
            "is_approved",
            "author_id",
            "author__first_name",
            "author__last_name",
            "approved_by__first_name",
            "approved_by__last_name",
            "approved_on",
            "is_ended",
            "created_on",
        )

        if user.is_admin:
            for poll in polls:
                image = (
                    UserDocuments.objects.filter(
                        owner_id=poll["author_id"], document_type="Profile Image"
                    )
                    .values("document_location")
                    .first()
                )
                poll["author_profile_image"] = image["document_location"]

        data = paginate_data(polls, page_number, 10)

        return JsonResponse(
            data,
            safe=False,
        )
