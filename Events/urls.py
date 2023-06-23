from django.urls import path

from .views.events_views import (CreateEvent, DeleteEvent, DeleteEventDocument,
                                 GetAllApprovedEvents, GetEventsByAuthor,
                                 UploadEventDocuments)

urlpatterns = [
    path("create-event/", CreateEvent.as_view(), name="Create Event"),
    path(
        "upload-event-documents/",
        UploadEventDocuments.as_view(),
        name="Upload Event Documents",
    ),
    path(
        "delete-event-documents/",
        DeleteEventDocument.as_view(),
        name="Delete Event Documents",
    ),
    path("delete-event/", DeleteEvent.as_view(), name="Delete Event"),
    path("my-events/", GetEventsByAuthor.as_view(), name="All Author Events"),
    path(
        "all-approved-events/",
        GetAllApprovedEvents.as_view(),
        name="All Approved Events",
    ),
]
