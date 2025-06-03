from typing import Dict, Optional, Literal
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class EncodeRequest(BaseModel):
    text: str
    key: str

class EncodeResponse(BaseModel):
    task_id: str

class DecodeRequest(BaseModel):
    encoded_data: str
    key: str
    huffman_codes: Dict[str, str]
    padding: int

class DecodeResponse(BaseModel):
    task_id: str

class TaskNotification(BaseModel):
    status: Literal["STARTED", "PROGRESS", "COMPLETED", "FAILED", "SUBSCRIBED"]
    task_id: str
    operation: Optional[Literal["encode", "decode"]] = None
    progress: Optional[int] = None
    result: Optional[dict] = None
    error: Optional[str] = None

class SubscribeMessage(BaseModel):
    action: Literal["subscribe"]
    task_id: str