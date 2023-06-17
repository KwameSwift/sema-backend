from django.urls import path

from .views.polls_view import CreatePoll


urlpatterns = [
    path(
        "create-poll/",
        CreatePoll.as_view(),
        name="Create A Poll",
    ),
]
