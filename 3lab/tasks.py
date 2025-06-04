from celery import Celery
import time
import json
from utils import huffman_encode, huffman_decode, xor_encrypt, xor_decrypt
import redis
import asyncio
from manager import manager  # Импортируем из нового файла

redis_client = redis.Redis(host='localhost', port=6379, db=0)

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')


@app.task(bind=True)
def encode_task(self, text: str, key: str, task_id: str):
    # Отправляем уведомление о начале
    asyncio.run(manager.send_message(task_id, {
        "status": "STARTED",
        "task_id": task_id,
        "operation": "encode"
    }))

    # Шаг 1: Кодирование Хаффмана
    asyncio.run(manager.send_message(task_id, {
        "status": "PROGRESS",
        "task_id": task_id,
        "operation": "encode",
        "progress": 25,
        "message": "Huffman encoding in progress..."
    }))
    encoded_data, huffman_codes, padding = huffman_encode(text)

    # Шаг 2: XOR шифрование
    asyncio.run(manager.send_message(task_id, {
        "status": "PROGRESS",
        "task_id": task_id,
        "operation": "encode",
        "progress": 50,
        "message": "XOR encryption in progress..."
    }))
    encrypted_data = xor_encrypt(encoded_data, key)

    # Шаг 3: Base64 кодирование
    asyncio.run(manager.send_message(task_id, {
        "status": "PROGRESS",
        "task_id": task_id,
        "operation": "encode",
        "progress": 75,
        "message": "Base64 encoding in progress..."
    }))
    base64_data = base64.b64encode(encrypted_data).decode('utf-8')

    result = {
        "encoded_data": base64_data,
        "key": key,
        "huffman_codes": huffman_codes,
        "padding": padding
    }

    asyncio.run(manager.send_message(task_id, {
        "status": "COMPLETED",
        "task_id": task_id,
        "operation": "encode",
        "result": result
    }))

    return result


@app.task(bind=True)
def decode_task(self, encoded_data: str, key: str, huffman_codes: dict, padding: int, task_id: str):
    # Отправляем уведомление о начале
    asyncio.run(manager.send_message(task_id, {
        "status": "STARTED",
        "task_id": task_id,
        "operation": "decode"
    }))

    # Шаг 1: Base64 декодирование
    asyncio.run(manager.send_message(task_id, {
        "status": "PROGRESS",
        "task_id": task_id,
        "operation": "decode",
        "progress": 25,
        "message": "Base64 decoding in progress..."
    }))
    encrypted_data = base64.b64decode(encoded_data.encode('utf-8'))

    # Шаг 2: XOR дешифрование
    asyncio.run(manager.send_message(task_id, {
        "status": "PROGRESS",
        "task_id": task_id,
        "operation": "decode",
        "progress": 50,
        "message": "XOR decryption in progress..."
    }))
    encoded_data = xor_decrypt(encrypted_data, key)

    # Шаг 3: Декодирование Хаффмана
    asyncio.run(manager.send_message(task_id, {
        "status": "PROGRESS",
        "task_id": task_id,
        "operation": "decode",
        "progress": 75,
        "message": "Huffman decoding in progress..."
    }))
    decoded_text = huffman_decode(encoded_data, huffman_codes, padding)

    result = {
        "decoded_text": decoded_text
    }

    asyncio.run(manager.send_message(task_id, {
        "status": "COMPLETED",
        "task_id": task_id,
        "operation": "decode",
        "result": result
    }))

    return result