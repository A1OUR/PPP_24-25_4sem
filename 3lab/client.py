import asyncio
import json
import websockets
import uuid
import aiohttp
from typing import Dict, Any

SERVER_URI = "ws://localhost:8000/ws/"
API_BASE_URL = "http://localhost:8000"


class ConsoleClient:
    def __init__(self):
        self.active_tasks: Dict[str, asyncio.Future] = {}

    async def send_request(self, operation: str, data: Dict[str, Any]) -> str:
        async with aiohttp.ClientSession() as session:
            url = f"{API_BASE_URL}/{operation}"
            async with session.post(url, json=data) as response:
                response_data = await response.json()
                return response_data["task_id"]

    async def listen_for_updates(self, task_id: str):
        try:
            async with websockets.connect(f"{SERVER_URI}{task_id}") as websocket:
                print(f"Connected to WebSocket for task {task_id}")
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    self.display_update(data)

                    if data["status"] == "COMPLETED":
                        return data["result"]
        except Exception as e:
            print(f"WebSocket error: {e}")

    def display_update(self, data: Dict[str, Any]):
        status = data["status"]
        task_id = data["task_id"]
        operation = data["operation"]

        if status == "STARTED":
            print(f"\nTask {task_id} ({operation}) started")
        elif status == "PROGRESS":
            progress = data["progress"]
            message = data.get("message", "")
            print(f"\rTask {task_id}: {message} {progress}%", end="")
        elif status == "COMPLETED":
            print(f"\nTask {task_id} completed!")
            print("Result:", json.dumps(data["result"], indent=2))

    async def encode_interactive(self):
        print("\n=== Encode Operation ===")
        text = input("Enter text to encode: ")
        key = input("Enter encryption key: ")

        task_id = await self.send_request("encode", {"text": text, "key": key})
        print(f"Task ID: {task_id}")

        await self.listen_for_updates(task_id)

    async def decode_interactive(self):
        print("\n=== Decode Operation ===")
        encoded_data = input("Enter encoded data (base64): ")
        key = input("Enter encryption key: ")
        huffman_codes = json.loads(input("Enter Huffman codes (JSON): "))
        padding = int(input("Enter padding: "))

        task_id = await self.send_request("decode", {
            "encoded_data": encoded_data,
            "key": key,
            "huffman_codes": huffman_codes,
            "padding": padding
        })
        print(f"Task ID: {task_id}")

        await self.listen_for_updates(task_id)

    async def run(self):
        while True:
            print("\n=== Main Menu ===")
            print("1. Encode text")
            print("2. Decode text")
            print("3. Exit")

            choice = input("Select an option (1-3): ")

            try:
                if choice == "1":
                    await self.encode_interactive()
                elif choice == "2":
                    await self.decode_interactive()
                elif choice == "3":
                    print("Exiting...")
                    break
                else:
                    print("Invalid choice, please try again.")
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    client = ConsoleClient()
    asyncio.run(client.run())