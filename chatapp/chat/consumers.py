import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Conversation
from outh.models import *
from rest_framework_simplejwt.tokens import AccessToken

# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Conversation
from outh.models import User
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import parse_qs

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract conversation_id from URL
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        # Get token from query string
        query_string = self.scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        # Authenticate user with JWT
        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token["user_id"]
                self.user = await database_sync_to_async(User.objects.get)(id=user_id)
                self.scope["user"] = self.user
            except Exception as e:
                print(f"Token authentication failed: {e}")
                await self.close(code=4001)  # Close with authentication error
                return
        else:
            print("No token provided")
            await self.close(code=4001)  # Close if no token
            return

        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close(code=4002)  # Close if user isn’t authenticated
            return

        # Join the room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
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

        # Broadcast message to group
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
        await self.send(text_data=json.dumps(event["message"]))