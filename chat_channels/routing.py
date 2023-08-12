from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from django.core.asgi import get_asgi_application
from .consumers import GroupChatConsumer

websocket_urlpatterns = URLRouter(
    [path("ws/forum-messages/<int:meeting_room_id>/", GroupChatConsumer.as_asgi())]
)

application = ProtocolTypeRouter(
    {"http": get_asgi_application(), "websocket": websocket_urlpatterns}
)
