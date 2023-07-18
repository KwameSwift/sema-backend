from django.db.models import ExpressionWrapper, F, FloatField, Q, Sum

from Polls.models.poll_models import Poll, PollChoices, PollVote


def retrieve_poll_with_choices(poll_id, type=None):
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
    if type:
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
