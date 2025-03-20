from rest_framework import generics, permissions, status, serializers
from .models import *
from .serializers import *
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from outh.models import User  # Directly use the imported User model
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user1=self.request.user) | Conversation.objects.filter(
            user2=self.request.user
        )

    def perform_create(self, serializer):
        try:
            user1 = User.objects.get(username=self.request.data.get("user1"))
            user2 = User.objects.get(username=self.request.data.get("user2"))
        except User.DoesNotExist:
            raise serializers.ValidationError("One or both users do not exist.")

        # Sort users by primary key
        user1, user2 = sorted([user1, user2], key=lambda u: u.pk)

        # Save the conversation
        conversation = serializer.save(user1=user1, user2=user2)

        # Notify WebSocket group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{conversation.id}",
            {
                "type": "chat_message",
                "message": {
                    "sender": user1.username,
                    "message": "Conversation started!",
                    "timestamp": str(conversation.created_at),
                },
            },
        )

        return conversation


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs["conversation_id"]
        return Message.objects.filter(conversation_id=conversation_id)

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)

        # Send the new message via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{message.conversation.id}",
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