from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# Send group messages
def send_group_message(meeting_room_id, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        meeting_room_id, {"type": "send_group_messages", "data": data}
    )
