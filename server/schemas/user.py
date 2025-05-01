from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserSettingsUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    alpaca_api_key: str | None = None
    alpaca_api_secret: str | None = None
    alpaca_base_url: str | None = None

class UserSettingsResponse(BaseModel):
    username: str
    email: str
    alpaca_api_key: str | None = None
    alpaca_api_secret: str | None = None
    alpaca_base_url: str | None = None

class UserBrokerSettingsUpdate(BaseModel):
    broker: str
    api_key: str
    api_secret: str
    base_url: str