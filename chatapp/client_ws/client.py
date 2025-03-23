# chat/management/commands/test_websocket.py
import asyncio
import websockets
import json
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Test WebSocket connection for a chat room'

    def add_arguments(self, parser):
        parser.add_argument('--room', type=str, default='room1', help='Chat room name')

    async def test_websocket(self, room):
        uri = f"ws://127.0.0.1:8001/ws/chat/{room}/"
        try:
            async with websockets.connect(uri) as websocket:
                print(f"Connected to {uri}")
                message = {"message": f"Hello from {room}!"}
                await websocket.send(json.dumps(message))
                print(f"Sent: {message}")
                async for response in websocket:
                    print(f"Received: {response}")
        except websockets.exceptions.InvalidStatus as e:
            print(f"Failed to connect: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def handle(self, *args, **options):
        room = options['room']
        asyncio.run(self.test_websocket(room))