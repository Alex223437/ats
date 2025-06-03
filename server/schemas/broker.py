from pydantic import BaseModel
from datetime import datetime

class UserBrokerSettingsUpdate(BaseModel):
    broker: str
    api_key: str
    api_secret: str
    base_url: str


class BrokerConnectionResponse(BaseModel):
    id: int
    broker: str
    base_url: str
    created_at: datetime

    class Config:
        from_attributes = True