import requests
import json
import asyncio
import websockets
import time
from typing import Optional

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/"


class EncryptionClient:
    def __init__(self):
        self.token = None
        self.user_id = None

    def login(self, username: str, password: str):
        response = requests.post(
            f"{BASE_URL}/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.user_id = username
            print("Login successful")
            return True
        else:
            print(f"Login failed: {response.text}")
            return False

    def encode(self, text: str, key: str) -> Optional[str]:
        if not self.token:
            print("Please login first")
            return None

        response = requests.post(
            f"{BASE_URL}/encode",
            json={"text": text, "key": key},
            headers={"Authorization": f"Bearer {self.token}"}
        )

        if response.status_code == 200:
            task_id = response.json()["task_id"]
            print(f"Encoding task started. Task ID: {task_id}")
            return task_id
        else:
            print(f"Error: {response.text}")
            return None

    def decode(self, encoded_data: str, key: str, huffman_codes: dict, padding: int) -> Optional[str]:
        if not self.token:
            print("Please login first")
            return None

        response = requests.post(
            f"{BASE_URL}/decode",
            json={
                "encoded_data": encoded_data,
                "key": key,
                "huffman_codes": huffman_codes,
                "padding": padding
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )

        if response.status_code == 200:
            task_id = response.json()["task_id"]
            print(f"Decoding task started. Task ID: {task_id}")
            return task_id
        else:
            print(f"Error: {response.text}")
            return None

    async def listen_for_task(self, task_id: str, timeout: int = 60):
        start_time = time.time()
        async with websockets.connect(f"{WS_URL}{self.user_id}") as websocket:
            # Subscribe to task updates
            await websocket.send(json.dumps({
                "action": "subscribe",
                "task_id": task_id
            }))

            while time.time() - start_time < timeout:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1)
                    data = json.loads(message)
                    if data.get("task_id") == task_id:
                        status = data.get("status")
                        if status == "COMPLETED":
                            print(f"\nTask {task_id} completed!")
                            print("Result:", data.get("result"))
                            return True
                        elif status == "FAILED":
                            print(f"\nTask {task_id} failed!")
                            print("Error:", data.get("error"))
                            return False
                        elif status == "PROGRESS":
                            print(f"\rProgress: {data.get('progress')}%", end="")
                except asyncio.TimeoutError:
                    continue

            print("\nTimeout reached")
            return False

    async def run_multiple_tasks(self):
        tasks = []
        while True:
            print("\n1. Add encode task")
            print("2. Add decode task")
            print("3. Run all tasks")
            print("4. Exit")

            choice = input("Select an option: ")

            if choice == "1":
                text = input("Enter text to encode: ")
                key = input("Enter encryption key: ")
                task_id = self.encode(text, key)
                if task_id:
                    tasks.append(task_id)

            elif choice == "2":
                encoded_data = input("Enter encoded data: ")
                key = input("Enter encryption key: ")
                huffman_codes = json.loads(input("Enter Huffman codes (as JSON): "))
                padding = int(input("Enter padding: "))
                task_id = self.decode(encoded_data, key, huffman_codes, padding)
                if task_id:
                    tasks.append(task_id)

            elif choice == "3":
                if not tasks:
                    print("No tasks added")
                    continue

                listeners = [self.listen_for_task(task_id) for task_id in tasks]
                await asyncio.gather(*listeners)
                tasks = []

            elif choice == "4":
                break


if __name__ == "__main__":
    client = EncryptionClient()

    # Simple login for testing
    if client.login("testuser", "secret"):
        asyncio.get_event_loop().run_until_complete(client.run_multiple_tasks())