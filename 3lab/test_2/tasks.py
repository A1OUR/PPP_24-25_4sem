from celery import Celery
from encryption import huffman_encode, huffman_decode, xor_encrypt, xor_decrypt
from websocket import manager
import time
import json

# Инициализация Celery с явными настройками
celery_app = Celery(
    'app.tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery_app.task(bind=True, name='app.tasks.process_encoding_task')
def process_encoding_task(self, user_id: str, text: str, key: str):
    try:
        # Явная проверка входных данных
        if not all([user_id, text, key]):
            raise ValueError("Missing required parameters")

        # Уведомление о начале
        manager.broadcast_task_update(
            self.request.id,
            {
                "status": "STARTED",
                "task_id": self.request.id,
                "operation": "encode"
            }
        )

        # Шаг 1: Кодирование Хаффмана
        huffman_data = huffman_encode(text)
        if not huffman_data or len(huffman_data) != 3:
            raise ValueError("Huffman encoding failed")

        huffman_encoded, huffman_codes, padding = huffman_data

        manager.broadcast_task_update(
            self.request.id,
            {
                "status": "PROGRESS",
                "task_id": self.request.id,
                "operation": "encode",
                "progress": 30
            }
        )

        # Шаг 2: XOR шифрование
        xor_encoded = xor_encrypt(huffman_encoded, key)
        if not xor_encoded:
            raise ValueError("XOR encryption failed")

        manager.broadcast_task_update(
            self.request.id,
            {
                "status": "PROGRESS",
                "task_id": self.request.id,
                "operation": "encode",
                "progress": 60
            }
        )

        # Результат
        result = {
            "encoded_data": xor_encoded,
            "key": key,
            "huffman_codes": huffman_codes,
            "padding": padding
        }

        manager.broadcast_task_update(
            self.request.id,
            {
                "status": "COMPLETED",
                "task_id": self.request.id,
                "operation": "encode",
                "result": result
            }
        )

        return result

    except Exception as e:
        error_msg = f"Encoding task failed: {str(e)}"
        if manager:
            manager.broadcast_task_update(
                self.request.id,
                {
                    "status": "FAILED",
                    "task_id": self.request.id,
                    "operation": "encode",
                    "error": error_msg
                }
            )
        raise