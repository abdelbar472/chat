from rest_framework import serializers
from .models import Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
