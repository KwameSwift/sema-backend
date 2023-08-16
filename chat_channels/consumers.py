import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from Forum.models import ChatRoom
from helpers.status_codes import non_existing_data_exception


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Socket Connected")
        chat_room_id = self.scope["url_route"]["kwargs"]["chat_room_id"]
        try:
            chat_room = ChatRoom.objects.get(id=chat_room_id)
            room_name = str(chat_room.room_name).lower().replace(" ", "_")
            await self.accept()
            await self.channel_layer.group_add(room_name, self.channel_name)
        except ChatRoom.DoesNotExist:
            raise non_existing_data_exception("Chat Room")

    async def disconnect(self, close_code):
        print("Socket Disconnected")
        chat_room_id = self.scope["url_route"]["kwargs"]["chat_room_id"]
        try:
            chat_room = ChatRoom.objects.get(id=chat_room_id)
            room_name = str(chat_room.room_name).lower().replace(" ", "_")
            await self.channel_layer.group_discard(room_name, self.channel_name)
        except ChatRoom.DoesNotExist:
            raise non_existing_data_exception("Chat Room")

    async def send_group_messages(self, event):
        await self.send(
            json.dumps(
                {
                    "data": event["data"],
                    "timestamp": datetime.now(),
                }
            )
        )
