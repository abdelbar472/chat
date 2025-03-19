import asyncio
import websockets
import json


async def chat_client():
    uri = "ws://127.0.0.1:8000/ws/chat/1/"  # Replace with the correct conversation ID
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server.")

        async def receive_messages():
            while True:
                response = await websocket.recv()
                message = json.loads(response)
                print(f"\nNew message from {message['sender']}: {message['content']}")

        async def send_messages():
            while True:
                message = input("Enter message: ").strip()
                if message.lower() == "exit":
                    print("Closing connection...")
                    break

                message_data = {"sender": "PythonClient", "content": message}
                await websocket.send(json.dumps(message_data))

        receive_task = asyncio.create_task(receive_messages())
        send_task = asyncio.create_task(send_messages())

        await send_task
        receive_task.cancel()  # Stop receiving when sending ends


asyncio.run(chat_client())
