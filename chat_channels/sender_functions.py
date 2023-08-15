from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# Send group messages
def send_group_message(chat_room, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        chat_room, {"type": "send_group_messages", "data": data}
    )
