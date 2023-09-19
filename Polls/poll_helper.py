import datetime

from django.db.models import ExpressionWrapper, F, FloatField, Q, Sum

from Forum.models import ForumPoll, ForumPollChoices, ForumPollVote
from Polls.models.poll_models import Poll, PollChoices, PollVote
from helpers.email_sender import send_email


def retrieve_poll_with_choices(poll_id, poll_type=None):
    # Retrieve the poll
    poll = Poll.objects.get(id=poll_id)

    # Calculate the total votes cast for the poll
    total_votes = (
        PollChoices.objects.filter(poll=poll).aggregate(total_votes=Sum("votes"))[
            "total_votes"
        ]
        or 0
    )

    if not total_votes:
        total_votes = 1

    # Retrieve the poll choices with their votes and percentages
    choices = (
        PollChoices.objects.filter(poll=poll)
        .annotate(
            choice_votes=Sum("votes"),
            vote_percentage=ExpressionWrapper(
                (F("votes") * 100.0) / total_votes,
                output_field=FloatField(),
            ),
        )
        .order_by("created_on")
    )

    # Create a dictionary representation of the poll
    # with choices and their votes/percentages
    if poll_type:
        poll_data = {
            "choices": [
                {
                    "choice_id": choice.id,
                    "choice": choice.choice,
                    "votes": choice.votes or 0,
                    "vote_percentage": round(choice.vote_percentage, 1)
                    if choice.vote_percentage
                    else 0,
                }
                for choice in choices
            ],
        }
    else:
        poll_data = {
            "id": poll.id,
            "file_location": poll.file_location,
            "snapshot_location": poll.snapshot_location,
            "question": poll.question,
            "start_date": poll.start_date,
            "end_date": poll.end_date,
            "is_ended": poll.is_ended,
            "author_id": poll.author_id,
            "author__first_name": poll.author.first_name,
            "author__last_name": poll.author.last_name,
            "author__is_verified": poll.author.is_verified,
            "author__profile_image": poll.author.profile_image,
            "approved_on": poll.approved_on,
            "created_on": poll.created_on,
            "choices": [
                {
                    "id": choice.id,
                    "choice": choice.choice,
                    "votes": choice.votes or 0,
                    "vote_percentage": round(choice.vote_percentage, 1)
                    if choice.vote_percentage
                    else 0,
                }
                for choice in choices
            ],
        }

    return poll_data


def get_polls_by_logged_in_user(user):
    data = []

    # Retrieve the poll
    polls = Poll.objects.filter(is_approved=True).values()

    for poll in polls:
        poll_vote = (
            PollVote.objects.filter(voter=user, poll_id=poll["id"])
            .values("poll_choice_id", "comments")
            .first()
        )
        if poll_vote:
            new_poll = retrieve_poll_with_choices(poll["id"])
            new_poll["voter_choice"] = poll_vote["poll_choice_id"]
            new_poll["voter_comments"] = poll_vote["comments"]
            data.append(new_poll)
        else:
            poll["choices"] = list(
                PollChoices.objects.filter(poll_id=poll["id"]).values("id", "choice")
            )
            data.append(poll)

    return data


def send_poll_declination_mail(poll, comments):
    subject = "Poll Declined"
    recipient_email = poll.author.email
    # Convert the string to a datetime object
    dt_object = datetime.datetime.fromisoformat(
        str(poll.created_on).replace("Z", "+00:00")
    )
    # Convert the datetime object to the desired format
    formatted_datetime = dt_object.strftime("%d-%b-%Y %H:%M:%S %Z")

    new_line = "\n"
    double_new_line = "\n\n"
    message = (
        f"Hi, {poll.author.first_name}.{new_line}"
        f"Your poll with the question: {poll.question}, created on {formatted_datetime} "
        f"has been declined.{new_line}"
        f"After a careful review of the poll, we realized it was in breach of our policies.{new_line}"
        f"Please find the reason for the declination below and act accordingly: {double_new_line}"
        f"{comments}"
        f"{double_new_line}"
        f"Thank you.{new_line}"
        f"The Sema Team"
    )

    send_email(recipient_email, subject, message)


def send_meeting_registration_mail(meeting, recipient_email, first_name):
    subject = "Virtual Meeting Registration"
    # Convert the string to a datetime object
    dt_object = datetime.datetime.fromisoformat(
        str(meeting.scheduled_start_time).replace("Z", "+00:00")
    )
    # Convert the datetime object to the desired format
    formatted_datetime = dt_object.strftime("%d-%b-%Y %H:%M:%S %Z")

    new_line = "\n"
    double_new_line = "\n\n"
    message = (
        f"Hi, {first_name}.{new_line}"
        f"Your registration to attend the virtual meeting: {meeting.meeting_agenda}, scheduled for"
        f" {formatted_datetime} has been received successfully. {new_line}"
        f"Please find details of the meeting below:{new_line}"
        f"Meeting link: {meeting.meeting_url}{new_line}"
        f"Agenda: {meeting.meeting_agenda}{new_line}"
        f"Organizer: {meeting.organizer.first_name} {meeting.organizer.last_name}{new_line}"
        f"Start date and time: {formatted_datetime}{new_line}"
        f"See you soon! {double_new_line}"
        f"Thank you.{new_line}"
        f"The Sema Team"
    )

    send_email(recipient_email, subject, message)


def retrieve_forum_poll_with_choices(poll_id, poll_type=None):
    # Retrieve the poll
    poll = ForumPoll.objects.get(id=poll_id)

    # Calculate the total votes cast for the poll
    total_votes = (
        ForumPollChoices.objects.filter(forum_poll=poll).aggregate(
            total_votes=Sum("votes")
        )["total_votes"]
        or 0
    )

    if not total_votes:
        total_votes = 1

    # Retrieve the poll choices with their votes and percentages
    choices = (
        ForumPollChoices.objects.filter(forum_poll=poll)
        .annotate(
            choice_votes=Sum("votes"),
            vote_percentage=ExpressionWrapper(
                (F("votes") * 100.0) / total_votes,
                output_field=FloatField(),
            ),
        )
        .order_by("created_on")
    )

    # Create a dictionary representation of the poll
    # with choices and their votes/percentages
    if poll_type:
        poll_data = {
            "choices": [
                {
                    "choice_id": choice.id,
                    "choice": choice.choice,
                    "votes": choice.votes or 0,
                }
                for choice in choices
            ],
        }
    else:
        poll_data = {
            "id": poll.id,
            "question": poll.question,
            "start_date": poll.start_date,
            "end_date": poll.end_date,
            "is_ended": poll.is_ended,
            # "author_id": poll.author_id,
            "author__first_name": poll.author.first_name,
            "author__last_name": poll.author.last_name,
            "author__is_verified": poll.author.is_verified,
            "author__profile_image": poll.author.profile_image,
            "created_on": poll.created_on,
            "choices": [
                {
                    "id": choice.id,
                    "choice": choice.choice,
                    "votes": choice.votes or 0,
                }
                for choice in choices
            ],
        }

    return poll_data


def get_forum_polls_by_logged_in_user(user, forum_id):
    data = []

    # Retrieve the poll
    polls = ForumPoll.objects.filter(forum_id=forum_id).values()

    for poll in polls:
        poll_vote = (
            ForumPollVote.objects.filter(voter=user, forum_poll_id=poll["id"])
            .values("poll_choice_id")
            .first()
        )
        if poll_vote:
            new_poll = retrieve_forum_poll_with_choices(poll["id"])
            new_poll["voter_choice"] = poll_vote["poll_choice_id"]
            data.append(new_poll)
        else:
            poll["choices"] = list(
                ForumPollChoices.objects.filter(forum_poll_id=poll["id"]).values(
                    "id", "choice"
                )
            )
            data.append(poll)

    return data


def author_retrieve_forum_poll_with_choices(poll_id, poll_type=None):
    # Retrieve the poll
    poll = ForumPoll.objects.get(id=poll_id)

    # Calculate the total votes cast for the poll
    total_votes = (
        ForumPollChoices.objects.filter(forum_poll=poll).aggregate(
            total_votes=Sum("votes")
        )["total_votes"]
        or 0
    )

    if not total_votes:
        total_votes = 1

    # Retrieve the poll choices with their votes and percentages
    choices = (
        ForumPollChoices.objects.filter(forum_poll=poll)
        .annotate(
            choice_votes=Sum("votes"),
            vote_percentage=ExpressionWrapper(
                (F("votes") * 100.0) / total_votes,
                output_field=FloatField(),
            ),
        )
        .order_by("created_on")
    )

    # Create a dictionary representation of the poll
    # with choices and their votes/percentages
    if poll_type:
        poll_data = {
            "choices": [
                {
                    "choice_id": choice.id,
                    "choice": choice.choice,
                    "votes": choice.votes or 0,
                }
                for choice in choices
            ],
        }
    else:
        poll_data = {
            "id": poll.id,
            "question": poll.question,
            "start_date": poll.start_date,
            "end_date": poll.end_date,
            "is_ended": poll.is_ended,
            "created_on": poll.created_on,
            "choices": [
                {
                    "id": choice.id,
                    "choice": choice.choice,
                    "votes": choice.votes or 0,
                }
                for choice in choices
            ],
        }

    return poll_data
