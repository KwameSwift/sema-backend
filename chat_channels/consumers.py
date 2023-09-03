import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from Forum.models import ChatRoom
from helpers.status_codes import non_existing_data_exception
from channels.db import database_sync_to_async


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        chat_room_id = self.scope["url_route"]["kwargs"]["chat_room_id"]
        chat_room = await self.get_chat_room(chat_room_id)
        room_name = self.get_room_name(chat_room)
        await self.channel_layer.group_add(room_name, self.channel_name)

    async def disconnect(self, close_code):
        chat_room_id = self.scope["url_route"]["kwargs"]["chat_room_id"]
        chat_room = await self.get_chat_room(chat_room_id)
        room_name = self.get_room_name(chat_room)
        await self.channel_layer.group_discard(room_name, self.channel_name)

    async def send_group_messages(self, event):
        await self.send(json.dumps({"data": event["data"]}))

    @database_sync_to_async
    def get_chat_room(self, chat_room_id):
        try:
            return ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            raise non_existing_data_exception("Chat Room")

    def get_room_name(self, chat_room):
        return str(chat_room.room_name).lower().replace(" ", "_")