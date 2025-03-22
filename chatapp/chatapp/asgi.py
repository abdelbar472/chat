import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing  # Ensure this imports your WebSocket routing
# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatapp.settings')

# Initialize Django
django.setup()

# Import WebSocket URL patterns after Django is initialized
from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),
})