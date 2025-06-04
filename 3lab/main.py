from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from manager import manager  # Импортируем из нового файла
import redis

app = FastAPI()

# Настройки CORS и Redis остаются без изменений
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class EncodeRequest(BaseModel):
    text: str
    key: str

class DecodeRequest(BaseModel):
    encoded_data: str
    key: str
    huffman_codes: Dict[str, str]
    padding: int

@app.post("/encode")
async def encode(request: EncodeRequest):
    from tasks import encode_task  # Ленивый импорт
    task_id = str(uuid.uuid4())
    task = encode_task.apply_async(args=[request.text, request.key, task_id], task_id=task_id)
    return {"task_id": task_id}

@app.post("/decode")
async def decode(request: DecodeRequest):
    from tasks import decode_task  # Ленивый импорт
    task_id = str(uuid.uuid4())
    task = decode_task.apply_async(
        args=[request.encoded_data, request.key, request.huffman_codes, request.padding, task_id],
        task_id=task_id
    )
    return {"task_id": task_id}

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await manager.connect(task_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(task_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)