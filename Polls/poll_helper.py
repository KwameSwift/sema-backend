from django.db.models import ExpressionWrapper, F, FloatField, Sum

from Polls.models.poll_models import Poll, PollChoices, PollVotes


def retrieve_poll_with_choices(poll_id, type=None):
    # Retrieve the poll
    poll = Poll.objects.get(id=poll_id)

    # Calculate the total votes cast for the poll
    total_votes = (
        PollVotes.objects.filter(poll=poll).aggregate(total_votes=Sum("votes"))[
            "total_votes"
        ]
        or 0
    )

    # Retrieve the poll choices with their votes and percentages
    choices = (
        PollChoices.objects.filter(poll=poll)
        .annotate(
            choice_votes=Sum("poll_choice__votes"),
            vote_percentage=ExpressionWrapper(
                (F("poll_choice__votes") * 100.0) / total_votes,
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
                    "votes": choice.choice_votes or 0,
                    "vote_percentage": round(choice.vote_percentage, 1)
                    if choice.vote_percentage
                    else 0,
                }
                for choice in choices
            ],
        }
    else:
        poll_data = {
            "poll_id": poll.id,
            "question": poll.question,
            "start_date": poll.start_date,
            "end_date": poll.end_date,
            "is_ended": poll.is_ended,
            "total_votes": total_votes,
            "author__first_name": poll.author.first_name,
            "author__last_name": poll.author.last_name,
            "created_on": poll.created_on,
            "choices": [
                {
                    "choice_id": choice.id,
                    "choice": choice.choice,
                    "votes": choice.choice_votes or 0,
                    "vote_percentage": round(choice.vote_percentage, 1)
                    if choice.vote_percentage
                    else 0,
                }
                for choice in choices
            ],
        }

    return poll_data
