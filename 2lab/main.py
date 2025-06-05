from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.encryption import router as encryption_router
from app.api.websocket import router as ws_router
import subprocess
import time

app = FastAPI(title="Encryption API") # создание класса фастапи

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"]) #  подключаем роутеры с эндпоинтами из файла auth
app.include_router(encryption_router, prefix="/api/encryption", tags=["Encryption"]) #  подключаем роутеры с эндпоинтами из файла ecrytption
app.include_router(ws_router, tags=["WebSocket"]) #  подключаем роутеры с эндпоинтами из файла websocket
