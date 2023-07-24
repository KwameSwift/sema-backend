from django.urls import path

from .views.meeting_room_views import (
    CreateMeetingRooms, DeleteMeetingRoom,
    GetMeetingRoom, UpdateMeetingRoom)

urlpatterns = [
    path("create-meeting-room/", CreateMeetingRooms.as_view(), name="Create A Meeting Room"),
    path("delete-meeting-room/<int:room_id>/", DeleteMeetingRoom.as_view(), name="Delete Meeting Room"),
    path("get-meeting-room/<int:room_id>/", GetMeetingRoom.as_view(), name="Get Meeting Room"),
    path("update-meeting-room/<int:room_id>/", UpdateMeetingRoom.as_view(), name="Update Meeting Room"),
]
