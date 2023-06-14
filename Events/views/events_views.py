import os

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models.user_model import User
from Events.models.events_model import Events
from helpers.functions import (delete_file, delete_local_file,
                               local_file_upload, paginate_data, upload_files)
from helpers.status_codes import (action_authorization_exception,
                                  cannot_perform_action,
                                  duplicate_data_exception,
                                  non_existing_data_exception)
from helpers.validations import check_permission, check_required_fields
from Utilities.models.documents_model import EventDocuments

LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")


# Create an Event
class CreateEvent(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data
        files = request.FILES.getlist("files")

        if not check_permission(user, "Events", [2]):
            raise action_authorization_exception("Unauthorized to create events")

        check_required_fields(data, ["event_name"])

        try:
            Events.objects.get(event_name=data["event_name"])
            raise duplicate_data_exception("Event with name")
        except Events.DoesNotExist:
            data["created_by"] = user
            event = Events.objects.create(**data)

            for file in files:
                full_directory = f"{LOCAL_FILE_PATH}{user.first_name}_{user.last_name}/Event_Documents/{event.event_name}"
                file_path = local_file_upload(full_directory, file)

                new_event_doc = {
                    "owner": user,
                    "event_id": event.id,
                    "document_location": file_path,
                }

                EventDocuments.objects.create(**new_event_doc)

            event_details = (
                Events.objects.filter(id=event.id)
                .values(
                    "id",
                    "event_name",
                    "venue",
                    "location",
                    "start_date",
                    "end_date",
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

            event["documnets"] = list(
                EventDocuments.objects.filter(event_id=event.id).values(
                    "id", "document_location"
                )
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
class UploadEventDocuments(APIView):
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

        for file in files:
            full_directory = f"{LOCAL_FILE_PATH}{user.first_name}_{user.last_name}/Event_Documents/{event.event_name}"
            file_path = local_file_upload(full_directory, file)

            new_event_image = {
                "owner": user,
                "event_id": event.id,
                "document_location": file_path,
            }

            EventDocuments.objects.create(**new_event_image)

        return JsonResponse(
            {"status": "success", "detail": "File(s) uploaded successfully"},
            safe=False,
        )


# Delete event image
class DeleteEventDocument(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data

        if not check_permission(user, "Events", [2]):
            raise action_authorization_exception("Unauthorized to delete event image")

        check_required_fields(data, ["event_id", "document_urls"])
        try:
            event = Events.objects.get(id=data["event_id"])
        except Events.DoesNotExist:
            raise non_existing_data_exception("Event")

        for url in data["document_urls"]:
            if os.path.exists(url):
                os.remove(url)
            EventDocuments.objects.filter(event=event, document_location=url).delete()

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

            events = EventDocuments.objects.filter(event_id=event.id).values(
                "document_location"
            )

            for doc in events:
                delete_local_file(doc["document_location"])

            EventDocuments.objects.filter(event_id=event.id).delete()

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

        for event in events:
            event["documents"] = list(
                EventDocuments.objects.filter(event_id=event["id"]).values(
                    "id", "document_location"
                )
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
        for event in events:
            event["documents"] = list(
                EventDocuments.objects.filter(event_id=event["id"]).values(
                    "id", "document_location"
                )
            )

        return JsonResponse(
            {
                "status": "success",
                "detail": "EVents retrieved successfully",
                "data": list(events),
            },
            safe=False,
        )
