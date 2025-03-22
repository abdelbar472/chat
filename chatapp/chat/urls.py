from django.urls import path, re_path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .consumers import *

urlpatterns = [
    path("conversations/", ConversationListCreateView.as_view(), name="conversation-list"),
    path("conversations/<int:conversation_id>/messages/", MessageListCreateView.as_view(), name="message-list"),
]

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<conversation_id>\d+)/$", ChatConsumer.as_asgi()),
]