import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.meetings.models import MeetingParticipant

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
        action = data.get("action")
        participant_id = data.get("participant_id")
        
        if action in ["join", "admit", "remove", "toggle_audio", "toggle_video", "raise_hand"]:
            await self.update_participant_state(action, participant_id, data)
            
        await self.channel_layer.group_send(
            self.meeting_group_name,
            {
                "type": "meeting_event",
                "data": data,
                "sender_channel_name": self.channel_name
            }
        )

    async def meeting_event(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))

    @database_sync_to_async
    def update_participant_state(self, action, participant_id, data):
        if not participant_id:
            return
        try:
            participant = MeetingParticipant.objects.get(id=participant_id)
            if action == "admit":
                participant.status = "JOINED"
                participant.save()
            elif action == "remove":
                participant.status = "REMOVED"
                participant.save()
            elif action == "toggle_audio":
                participant.is_audio_on = data.get("is_audio_on", participant.is_audio_on)
                participant.save()
            elif action == "toggle_video":
                participant.is_video_on = data.get("is_video_on", participant.is_video_on)
                participant.save()
            elif action == "raise_hand":
                participant.has_raised_hand = data.get("has_raised_hand", participant.has_raised_hand)
                participant.save()
        except MeetingParticipant.DoesNotExist:
            pass
