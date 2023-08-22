from django.urls import path

from .views.chat_room_views import (
    CreateChatRooms,
    DeleteChatRoom,
    GetChatRoom,
    UpdateChatRoom,
    LeaveChatRoom,
    JoinChatRoom,
    SendMessageToChatRoom,
)

urlpatterns = [
    path(
        "create-chat-room/<int:forum_id>/",
        CreateChatRooms.as_view(),
        name="Create A Chat Room",
    ),
    path(
        "delete-chat-room/<int:room_id>/",
        DeleteChatRoom.as_view(),
        name="Delete Chat Room",
    ),
    path(
        "get-chat-room/<int:room_id>/",
        GetChatRoom.as_view(),
        name="Get Chat Room",
    ),
    path(
        "update-chat-room/<int:room_id>/",
        UpdateChatRoom.as_view(),
        name="Update Chat Room",
    ),
    path(
        "update-chat-room/<int:room_id>/",
        UpdateChatRoom.as_view(),
        name="Update Chat Room",
    ),
    path(
        "join-chat-room/<int:room_id>/",
        JoinChatRoom.as_view(),
        name="Join Chat Room",
    ),
    path(
        "leave-chat-room/<int:room_id>/",
        LeaveChatRoom.as_view(),
        name="Leave Chat Room",
    ),
    path(
        "send-message/<int:room_id>/",
        SendMessageToChatRoom.as_view(),
        name="Send Message To Chat Room",
    ),
]
