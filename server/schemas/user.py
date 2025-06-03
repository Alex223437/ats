from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic import field_validator

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain letters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digits")
        return v


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
    created_at: datetime


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