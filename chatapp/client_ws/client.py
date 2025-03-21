import asyncio
import websockets
import json

async def chat_client():
    token = "your-jwt-token-here"  # Replace with actual token
    uri = f"ws://127.0.0.1:8001/ws/chat/1/?token={token}"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server")
        message = {"message": "Hello from client!"}
        await websocket.send(json.dumps(message))
        print(f"Sent: {message}")
        async for response in websocket:
            print(f"Received: {response}")

asyncio.run(chat_client())