from rest_framework import serializers
from outh.models import User
from .models import *



class ConversationSerializer(serializers.ModelSerializer):
    user1 = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())
    user2 = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())

    class Meta:
        model = Conversation
        fields = ["id", "user1", "user2", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "content", "timestamp", "status"]
