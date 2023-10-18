from django.urls import path

from .views.polls_view import (
    CreatePoll,
    DeletePoll,
    GetAllApprovedPolls,
    GetAllPollResults,
    SearchPolls,
    UpdatePoll,
    VoteOnAPoll,
    UpdateUserPollComment,
)

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
        "all-approved-polls/<int:page_number>/",
        GetAllApprovedPolls.as_view(),
        name="Get All Approved Polls",
    ),
    path(
        "update-poll/<int:poll_id>/",
        UpdatePoll.as_view(),
        name="Update Poll",
    ),
    path(
        "update-poll-comment/<int:poll_id>/",
        UpdateUserPollComment.as_view(),
        name="Update Poll Comment",
    ),
    path(
        "search-polls/<int:page_number>/",
        SearchPolls.as_view(),
        name="Search Polls",
    ),
]
