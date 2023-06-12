from django.urls import path

from .views.events_views import CreateEvent, DeleteEventImage, UploadEventImage

urlpatterns = [
    path("create-event/", CreateEvent.as_view(), name="Create Event"),
    path("upload-event-image/", UploadEventImage.as_view(), name="Upload Event Image"),
    path("delete-event-image/", DeleteEventImage.as_view(), name="Delete Event Image"),
]
