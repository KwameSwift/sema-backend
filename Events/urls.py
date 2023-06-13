from django.urls import path

from .views.events_views import (
    CreateEvent, GetAllApprovedEvents,
    DeleteEventImage,
    UploadEventImage,
    DeleteEvent,
    GetEventsByAuthor
)

urlpatterns = [
    path("create-event/", CreateEvent.as_view(), name="Create Event"),
    path("upload-event-image/", UploadEventImage.as_view(), name="Upload Event Image"),
    path("delete-event-image/", DeleteEventImage.as_view(), name="Delete Event Image"),
    path("delete-event/", DeleteEvent.as_view(), name="Delete Event"),
    path("my-events/", GetEventsByAuthor.as_view(), name="All Author Events"),
    path("all-approved-events/", GetAllApprovedEvents.as_view(), name="All Approved Events"),
]
