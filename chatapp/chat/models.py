from outh.models import *
from django.db import models






class Conversation(models.Model):
    user1 = models.ForeignKey(User, related_name="conversations_initiated", on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name="conversations_received", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')  # Prevent duplicate conversations

    def __str__(self):
        return f"Conversation between {self.user1.username} and {self.user2.username}"


class Message(models.Model):
    conversation = models.ForeignKey("Conversation", on_delete=models.CASCADE, null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=[('sent', 'Sent'), ('delivered', 'Delivered'), ('read', 'Read')], default='sent'
    )

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"