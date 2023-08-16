from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from django.core.asgi import get_asgi_application
from .consumers import ChatRoomConsumer

websocket_urlpatterns = URLRouter(
    [path("ws/forum-messages/<int:chat_room_id>/", ChatRoomConsumer.as_asgi())]
)

application = ProtocolTypeRouter(
    {"http": get_asgi_application(), "websocket": websocket_urlpatterns}
)
