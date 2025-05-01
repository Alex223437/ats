from pydantic import BaseModel

class StockBase(BaseModel):
    ticker: str

class StockCreate(StockBase):
    pass  # Может быть полезно, если потребуется добавить валидацию

class StockResponse(StockBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True