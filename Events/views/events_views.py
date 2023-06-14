import os

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models.user_model import User
from Events.models.events_model import Events
from helpers.functions import delete_file, paginate_data, upload_files
from helpers.status_codes import (action_authorization_exception,
                                  cannot_perform_action,
                                  duplicate_data_exception,
                                  non_existing_data_exception)
from helpers.validations import check_permission, check_required_fields


# Create an Event
class CreateEvent(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data

        if not check_permission(user, "Events", [2]):
            raise action_authorization_exception("Unauthorized to create events")

        check_required_fields(data, ["event_name"])

        try:
            Events.objects.get(event_name=data["event_name"])
            raise duplicate_data_exception("Event with name")
        except Events.DoesNotExist:
            data["created_by"] = user
            event = Events.objects.create(**data)

            event_details = (
                Events.objects.filter(id=event.id)
                .values(
                    "id",
                    "event_name",
                    "venue",
                    "location",
                    "start_date",
                    "end_date",
                    "event_image",
                    "description",
                    "is_approved",
                    "created_by__first_name",
                    "created_by__last_name",
                    "approved_by__first_name",
                    "approved_by__last_name",
                    "created_on",
                )
                .first()
            )

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Event created successfully",
                    "data": event_details,
                },
                safe=False,
            )


# Upload events image
class UploadEventImage(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist("files")
        data = request.data
        user = self.request.user

        if not check_permission(user, "Events", [2]):
            raise action_authorization_exception("Unauthorized to upload event image")

        check_required_fields(data, ["event_id"])

        try:
            event = Events.objects.get(id=data["event_id"])
        except Events.DoesNotExist:
            raise non_existing_data_exception("Event")

        LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")
        for file in files:
            file_name = str(file.name)
            new_name = file_name.replace(" ", "_")
            fs = FileSystemStorage(location=LOCAL_FILE_PATH)
            fs.save(new_name, file)

            file_path = LOCAL_FILE_PATH + new_name

            subdirectory = f"Events/Documents/Event_Images/{event.event_name}"
            uploaded_path = upload_files(file_path, subdirectory)

            event.event_image = uploaded_path
            event.save()
            if os.path.exists(file_path):
                os.remove(file_path)

        return JsonResponse(
            {"status": "success", "detail": "File uploaded successfully"},
            safe=False,
        )


# Delete event image
class DeleteEventImage(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data

        if not check_permission(user, "Events", [2]):
            raise action_authorization_exception("Unauthorized to delete event image")

        check_required_fields(data, ["event_id"])
        try:
            event = Events.objects.get(id=data["event_id"])
            if event.created_by != user:
                raise action_authorization_exception(
                    "Unauthorized to delete image for this event"
                )
        except Events.DoesNotExist:
            raise non_existing_data_exception("Event")

        delete_file(event.event_image)

        event.event_image = None
        event.save()

        return JsonResponse(
            {"status": "success", "detail": "File deleted successfully"},
            safe=False,
        )


# Delete event
class DeleteEvent(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data

        if not check_permission(user, "Events", [2]):
            raise action_authorization_exception("Unauthorized to delete event")

        check_required_fields(data, ["event_id"])
        try:
            event = Events.objects.get(id=data["event_id"])

            delete_file(event.event_image)

            event.delete()

            return JsonResponse(
                {"status": "success", "detail": "Event deleted successfully"},
                safe=False,
            )
        except Events.DoesNotExist:
            raise non_existing_data_exception("Event")


# Get my events
class GetEventsByAuthor(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        page_number = self.kwargs.get("page_number")

        if not check_permission(user, "Events", [1, 2]):
            raise action_authorization_exception("Unauthorized to delete event")

        events = (
            Events.objects.filter(created_by=user)
            .values(
                "id",
                "venue",
                "location",
                "start_date",
                "end_date",
                "description",
                "event_links",
                "is_approved",
                "created_on",
            )
            .order_by("-created_on")
        )

        data = paginate_data(events, page_number, 10)
        return JsonResponse(
            data,
            safe=False,
        )


# Get all approved events
class GetAllApprovedEvents(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        events = (
            Events.objects.filter(is_approved=True)
            .values(
                "id",
                "event_name",
                "venue",
                "location",
                "start_date",
                "end_date",
                "event_image",
                "description",
                "is_approved",
                "created_by__first_name",
                "created_by__last_name",
                "approved_by__first_name",
                "approved_by__last_name",
                "created_on",
            )
            .order_by("-created_on")
        )

        return JsonResponse(
            {
                "status": "success",
                "detail": "EVents retrieved successfully",
                "data": list(events),
            },
            safe=False,
        )
