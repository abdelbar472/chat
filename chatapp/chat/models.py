from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Conversation(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_started')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_joined')
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="unread")  # Example: "read", "unread"
