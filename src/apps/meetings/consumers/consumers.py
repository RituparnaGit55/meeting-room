from channels.generic.websocket import AsyncWebsocketConsumer
import json


class MeetingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.meeting_id = self.scope["url_route"]["kwargs"]["meeting_id"]
        self.meeting_group_name = f"meeting_{self.meeting_id}"
        await self.channel_layer.group_add(
            self.meeting_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.meeting_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.meeting_group_name,
            {
                "type": "meeting_event",
                "data": data
            }
        )

    async def meeting_event(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))
