from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.stock import UserStock
from models.user import User
from routes.auth import get_current_user  # ✅ Импорт get_current_user

user_stock_router = APIRouter(prefix="/users/me/stocks", tags=["user_stocks"])

@user_stock_router.get("/")
async def get_user_stocks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the user's tracked stocks."""
    stocks = db.query(UserStock).filter(UserStock.user_id == user.id).all()
    return {"stocks": [stock.ticker for stock in stocks]}

@user_stock_router.post("/add")
async def add_user_stock(ticker: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add a stock to the user's tracking list."""
    if db.query(UserStock).filter(UserStock.user_id == user.id, UserStock.ticker == ticker).first():
        raise HTTPException(status_code=400, detail="Stock already exists")

    new_stock = UserStock(user_id=user.id, ticker=ticker)
    db.add(new_stock)
    db.commit()
    return {"message": "Stock added successfully"}

@user_stock_router.delete("/remove")
async def remove_user_stock(ticker: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Remove a stock from the user's tracking list."""
    stock = db.query(UserStock).filter(UserStock.user_id == user.id, UserStock.ticker == ticker).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    db.delete(stock)
    db.commit()
    return {"message": "Stock removed successfully"}