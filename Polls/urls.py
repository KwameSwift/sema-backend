from django.urls import path

from .views.polls_view import (CreatePoll, GetAllApprovedPolls,
                               GetAllPollResults, VoteOnAPoll)

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
]
