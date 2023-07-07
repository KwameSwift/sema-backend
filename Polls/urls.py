from django.urls import path

from .views.polls_view import (CreatePoll, GetAllApprovedPolls,
                               GetAllPollResults, VoteOnAPoll, UpdatePoll)

urlpatterns = [
    path(
        "create-poll/",
        CreatePoll.as_view(),
        name="Create A Poll",
    ),
    path(
        "vote-on-poll/",
        VoteOnAPoll.as_view(),
        name="Vote On A Poll",
    ),
    path(
        "all-polls-results/",
        GetAllPollResults.as_view(),
        name="Get All Polls And Results",
    ),
    path(
        "all-approved-polls/",
        GetAllApprovedPolls.as_view(),
        name="Get All Approved Polls",
    ),
    path(
        "update-poll/<int:poll_id>/",
        UpdatePoll.as_view(),
        name="Update Poll",
    ),
]
