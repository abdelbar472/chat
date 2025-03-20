import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Conversation
from outh.models import *


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        # Add user to the WebSocket group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove user from the WebSocket group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender_username = data["sender"]
        content = data["content"]

        sender = await database_sync_to_async(User.objects.get)(username=sender_username)
        conversation = await database_sync_to_async(Conversation.objects.get)(id=self.conversation_id)

        # Save message to database
        message = await database_sync_to_async(Message.objects.create)(
            conversation=conversation, sender=sender, content=content
        )

        # Broadcast message to WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": {
                    "id": message.id,
                    "conversation": message.conversation.id,
                    "sender": message.sender.username,
                    "content": message.content,
                    "timestamp": str(message.timestamp),
                    "status": message.status,
                },
            },
        )

    async def chat_message(self, event):
        # Send message data to WebSocket clients
        await self.send(text_data=json.dumps(event["message"]))
