from fastapi import FastAPI, Depends, HTTPException, WebSocket
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import Dict, Any
import asyncio

from auth import authenticate_user, create_access_token, get_current_user
from models import User, Token, EncodeRequest, EncodeResponse, DecodeRequest, DecodeResponse
from websocket import manager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/encode", response_model=EncodeResponse)
async def encode_data(
    request: EncodeRequest,
    current_user: User = Depends(get_current_user)
):
    from tasks import process_encoding_task
    task = process_encoding_task.delay(current_user.username, request.text, request.key)
    return {"task_id": task.id}

@app.post("/decode", response_model=DecodeResponse)
async def decode_data(
    request: DecodeRequest,
    current_user: User = Depends(get_current_user)
):
    from tasks import process_decoding_task
    task = process_decoding_task.delay(
        current_user.username,
        request.encoded_data,
        request.key,
        request.huffman_codes,
        request.padding
    )
    return {"task_id": task.id}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("action") == "subscribe":
                    task_id = message["task_id"]
                    manager.subscribe_to_task(user_id, task_id)
                    await manager.send_message(
                        user_id,
                        {
                            "status": "SUBSCRIBED",
                            "task_id": task_id
                        }
                    )
            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(user_id)