import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Conversation
from outh.models import User
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import parse_qs

# This is a WebSocket consumer that handles real-time chat messages between 2 users
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()

        await self.channel_layer.group_add(
            f'conversation_{self.conversation_id}',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f'conversation_{self.conversation_id}',
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Save message to database
        await self.save_message(message)

        # Broadcast message to conversation group
        await self.channel_layer.group_send(
            f'conversation_{self.conversation_id}',
            {
                'type': 'chat.message',
                'message': message,
                'sender': self.user.username,
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
        }))

    @database_sync_to_async
    def save_message(self, message):
        conversation = Conversation.objects.get(id=self.conversation_id)
        Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=message
        )

    @database_sync_to_async
    def save_message(self, message):
        conversation = Conversation.objects.get(id=self.conversation_id)
        Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=message,
            status="unread"  # Add status
        )
