from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.chat.models import Message
from apps.accounts.models import User
from apps.meetings.models import Meeting
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.meeting_id = self.scope["url_route"]["kwargs"]["meeting_id"]
        # Use query string or connect message for participant ID if needed,
        # but standard group is enough if we filter on frontend or send specific events.
        self.chat_group_name = f"chat_{self.meeting_id}"
        
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        
        if action == "chat_message":
            # Save message to DB
            msg_data = await self.save_message(data)
            
            # Broadcast to everyone in the room
            # The frontend will check `is_private` and `receiver_id` to display appropriately
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    "type": "chat_message",
                    "message": msg_data
                }
            )

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "action": "chat_message",
            "message": message
        }))

    @database_sync_to_async
    def save_message(self, data):
        meeting = Meeting.objects.filter(meeting_id=self.meeting_id).first()
        if not meeting:
            return data
            
        sender_id = data.get("sender_id")
        sender_name = data.get("sender_name")
        receiver_id = data.get("receiver_id")
        is_private = data.get("is_private", False)
        content = data.get("content", "")
        file_url = data.get("file_url")
        file_type = data.get("file_type")
        file_name = data.get("file_name")
        
        user = User.objects.filter(id=sender_id).first() if sender_id else None
        receiver = User.objects.filter(id=receiver_id).first() if receiver_id else None
        
        # Don't create DB object if it's already created via file upload view (which might pass message_id)
        message_id = data.get("message_id")
        
        if message_id:
            msg = Message.objects.filter(id=message_id).first()
        else:
            msg = Message.objects.create(
                meeting=meeting,
                user=user,
                sender_name=sender_name,
                receiver=receiver,
                is_private=is_private,
                content=content,
            )
            
        return {
            "id": msg.id,
            "sender_id": user.id if user else None,
            "sender_name": sender_name or (user.first_name if user else "Guest"),
            "receiver_id": receiver.id if receiver else None,
            "is_private": is_private,
            "content": content,
            "file_url": file_url,
            "file_type": file_type,
            "file_name": file_name,
            "timestamp": msg.timestamp.isoformat()
        }
