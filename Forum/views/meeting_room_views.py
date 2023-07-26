import os

from django.http import JsonResponse
from google_auth_oauthlib.flow import Flow
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Forum.models import MeetingRoom
from helpers.status_codes import action_authorization_exception, duplicate_data_exception, cannot_perform_action, \
    non_existing_data_exception
from helpers.validations import check_permission, check_required_fields
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


class CreateMeetingRooms(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data
        user = self.request.user

        if not check_permission(user, "Forums", [2]):
            raise action_authorization_exception("Unauthorized to create meeting room")

        check_required_fields(data, ["room_name", "description"])

        try:
            MeetingRoom.objects.get(room_name=data["room_name"], creator=user)
            raise duplicate_data_exception("Meeting Room")
        except MeetingRoom.DoesNotExist:
            meeting_room = MeetingRoom.objects.create(
                room_name=data["room_name"],
                description=data["description"],
                creator=user
            )

            data = {
                "id": meeting_room.id,
                "room_name": meeting_room.room_name,
                "description": meeting_room.description
            }

            return JsonResponse(
                {
                    "status": "success",
                    "detail": "Meeting Room created successfully",
                    "data": data
                },
                safe=False,
            )


class DeleteMeetingRoom(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        room_id = self.kwargs["room_id"]

        try:
            meeting_room = MeetingRoom.objects.get(id=room_id)
            if user.user_key == meeting_room.creator_id:
                meeting_room.delete()

                return JsonResponse(
                    {"status": "success", "detail": "Meeting Room deleted successfully"},
                    safe=False,
                )
            else:
                raise cannot_perform_action("Cannot delete this meeting room")

        except MeetingRoom.DoesNotExist:
            raise duplicate_data_exception("Meeting Room")


class GetMeetingRoom(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        room_id = self.kwargs["room_id"]

        try:
            meeting_room = (
                MeetingRoom.objects.filter(id=room_id)
                .values(
                    "id", "room_name",
                    "description", "creator_id",
                    "creator__first_name", "creator__last_name",
                    "creator__is_verified", "creator__profile_image",
                    "created_on"
                )
            )

            return JsonResponse(
                {"status": "success",
                 "detail": "Meeting Room retrieved successfully",
                 "data": meeting_room[0]
                 },
                safe=False,
            )
        except IndexError:
            raise non_existing_data_exception("Meeting Room")


class UpdateMeetingRoom(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data
        room_id = self.kwargs["room_id"]

        if not check_permission(user, "Forums", [2]):
            raise action_authorization_exception("Unauthorized to create meeting room")

        try:
            MeetingRoom.objects.get(id=room_id)
            MeetingRoom.objects.filter(id=room_id).update(**data)

            return JsonResponse(
                {"status": "success",
                 "detail": "Meeting Room updated successfully"
                 },
                safe=False,
            )
        except MeetingRoom.DoesNotExist:
            raise non_existing_data_exception("Meeting Room")


class GenerateGoogleMeet(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data


SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_google_meet(request):
    data = request.data
    
    check_required_fields(data, ["event_summary", "start_date", "end_date"])

    # Create the Flow instance
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id":  os.environ.get("GOOGLE_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": [os.environ.get("GOOGLE_REDIRECT_URI")],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token"
            }
        },
        scopes=SCOPES
    )

    # Check if the user has granted access to their Google Calendar
    credentials = Credentials.from_authorized_user_info(
        request.session.get('google_credentials', None),
        scopes=SCOPES
    )

    if not credentials or not credentials.valid:
        # If the token is not valid or not found, redirect the user to the authorization URL
        auth_url, _ = flow.authorization_url()
        return JsonResponse(
                {"status": "success",
                 "detail": "Meeting updated successfully",
                 "authorization_url": auth_url
                 },
                safe=False,
            )
      

    # If the user is authenticated, generate the Google Meet link
    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': data["event_summary"],
        'start': {
            'dateTime': data["start_date"],
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': data["end_date"],
            'timeZone': 'UTC',
        },
        'conferenceData': {
            'createRequest': {
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet',
                },
                'requestId': 'random_string',  # Use a random string here
            },
        },
    }

    event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
    meet_link = event['hangoutLink']

    # Return event details along with the Meet link
    return JsonResponse(
        {"status": "success",
            "detail": "Meeting updated successfully",
            "data": meet_link
            },
        safe=False,
    )

    return JsonResponse(event_details, status=201)
