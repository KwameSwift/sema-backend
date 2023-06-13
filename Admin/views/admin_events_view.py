import datetime

from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Events.models.events_model import Events
from helpers.functions import aware_datetime, paginate_data
from helpers.status_codes import (action_authorization_exception,
                                  cannot_perform_action,
                                  non_existing_data_exception)
from helpers.validations import check_required_fields, check_super_admin


# Get all events by admin
class GetAllEventsAsAdmin(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        page_number = self.kwargs.get("page_number")

        if not check_super_admin(user):
            raise action_authorization_exception("Unauthorized to view Events")

        events = (
            Events.objects.all()
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

        data = paginate_data(events, page_number, 10)
        return JsonResponse(
            data,
            safe=False,
        )


# Approve Events
class ApproveEvents(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data

        # Check if user is super admin
        if not check_super_admin(self.request.user):
            raise cannot_perform_action("Unauthorized to perform action")

        check_required_fields(data, ["event_id"])

        try:
            event = Events.objects.get(id=data["event_id"])
            event.is_approved = True
            event.approved_by = user
            event.updated_on = aware_datetime(datetime.datetime.now())
            event.save()

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Event approved",
                },
                safe=False,
            )
        except Events.DoesNotExist:
            raise non_existing_data_exception("Event")
