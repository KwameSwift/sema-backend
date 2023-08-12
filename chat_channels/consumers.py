import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Socket Connected")
        meeting_room = self.scope["url_route"]["kwargs"]["meeting_room_id"]
        await self.accept()
        await self.channel_layer.group_add(meeting_room, self.channel_name)

    async def disconnect(self, close_code):
        print("Socket Disconnected")
        meeting_room = self.scope["url_route"]["kwargs"]["meeting_room_id"]
        await self.channel_layer.group_discard(meeting_room, self.channel_name)

    async def send_group_messages(self, event):
        await self.send(
            json.dumps(
                {
                    "data": event["data"],
                    "timestamp": datetime.now(),
                }
            )
        )
