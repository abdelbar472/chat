from django.urls import path
from .views import *

urlpatterns = [
    path("conversations/", ConversationListCreateView.as_view(), name="conversation-list"),
    path("messages/<int:conversation_id>/", MessageListCreateView.as_view(), name="message-list"),
    path("ws-token/<int:conversation_id>/", WebSocketTokenView.as_view(), name="ws-token"),
    path('<int:conversation_id>/', chat_view, name='chat'),  # Fix reference to chat_view
]