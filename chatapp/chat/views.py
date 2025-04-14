from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class WebSocketTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, conversation_id):
        token = str(AccessToken.for_user(request.user))
        return Response({
            "conversation_id": conversation_id,
            "token": token
        })

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user1=self.request.user) | Conversation.objects.filter(user2=self.request.user)

    def perform_create(self, serializer):
        conversation = Conversation.objects.get(id=self.kwargs["conversation_id"])
        serializer.save(sender=self.request.user, conversation=conversation, status="unread")

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(conversation_id=self.kwargs["conversation_id"])

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

def chat_view(request, conversation_id):
    token = str(AccessToken.for_user(request.user))
    return render(request, 'chat/chat.html', {
        'conversation_id': conversation_id,
        'token': token
    })