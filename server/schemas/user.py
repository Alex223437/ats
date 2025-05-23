from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  


class UserSettingsUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None  


class UserSettingsResponse(BaseModel):
    username: str
    email: EmailStr


class UserBrokerSettingsUpdate(BaseModel):
    broker: str
    api_key: str
    api_secret: str
    base_url: str

class BrokerConnectionInfo(BaseModel):
    id: int
    broker: str
    is_connected: bool
    created_at: datetime

    class Config:
        from_attributes = True