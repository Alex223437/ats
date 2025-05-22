from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
import asyncio
from sqlalchemy.orm import Session
from services.data_analysis_service import DataAnalysisService
from services.strategy_service import StrategyService
from data.market_data import MarketData
from database import get_db
from models.strategy import Strategy
from models.user import User
from models.strategy_ticker import StrategyTicker
from routes.auth import get_current_user  

stock_router = APIRouter()


@stock_router.get("/api/data/{ticker}")
async def get_stock_data(
    ticker: str,
    strategy_id: str | None = Query(None),
    raw: bool = Query(False)  
):
    try:
        if raw:
            result = await asyncio.to_thread(MarketData.download_data, ticker)
        else:
            result = await asyncio.to_thread(DataAnalysisService.get_strategy_result, ticker, strategy_id)

        result = result.reset_index()
        result['Date'] = result['Date'].dt.strftime('%Y-%m-%d')

        response_columns = ['Date', 'Close']
        for col in ['Buy_Signal', 'Sell_Signal', 'SMA_Short', 'SMA_Long']:
            if col in result.columns:
                result[col] = result[col].astype(bool) if 'Signal' in col else result[col]
                response_columns.append(col)

        response = result[response_columns].to_dict(orient='records')
        return JSONResponse(content={"data": response})
    
    except Exception as e:
        print(f"❌ Server error: {e}")  
        return JSONResponse(content={"error": str(e)}, status_code=500)

@stock_router.get("/api/indicators/{ticker}")
async def get_indicators(ticker: str):
    try:
        df = await asyncio.to_thread(
            MarketData.download_data, ticker, from_date="2024-01-01", to_date="2025-03-25"
        )

        if df is None or df.empty:
            raise HTTPException(status_code=500, detail="Данные не найдены")

        latest = df.iloc[-1]

        indicators = {
            "SMA_10": round(latest.get("SMA_10", 0), 2),
            "SMA_50": round(latest.get("SMA_50", 0), 2),
            "EMA_10": round(latest.get("EMA_10", 0), 2),
            "EMA_50": round(latest.get("EMA_50", 0), 2),
            "RSI_14": round(latest.get("RSI_14", 0), 2),
            "MACD": round(latest.get("MACD", 0), 2),
            "MACD_Signal": round(latest.get("MACD_Signal", 0), 2)
        }

        return JSONResponse(content=indicators)

    except Exception as e:
        print(f"❌ Indicators error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ✅ Новый эндпоинт для Ticker Overview
@stock_router.get("/stocks/overview")
def get_stock_overview(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    def get_latest_from_series_or_dict(obj):
        if isinstance(obj, dict) and obj:
            return round(obj[max(obj)], 2)
        elif hasattr(obj, "iloc") and not obj.empty:
            return round(obj.iloc[-1], 2)
        return None

    try:
        response = []

        for user_stock in user.stocks:
            ticker = user_stock.ticker
            price = 0.0
            rsi = ema_10 = None
            signal = None
            strategy_title = None

            # Привязка стратегии
            strategy_link = (
                db.query(Strategy)
                .join(StrategyTicker, Strategy.id == StrategyTicker.strategy_id)
                .filter(
                    Strategy.user_id == user.id,
                    Strategy.is_enabled == True,
                    StrategyTicker.user_stock_id == user_stock.id
                )
                .first()
            )

            data = MarketData.download_data(ticker)
            if data is None or data.empty:
                continue

            # Текущая цена
            price = round(data["Close"].iloc[-1], 2)

            # RSI и EMA как словари с датами
            rsi = get_latest_from_series_or_dict(data.get("RSI_14"))
            ema_10 = get_latest_from_series_or_dict(data.get("EMA_10"))

            # Стратегия и сигнал
            if strategy_link:
                strategy_title = strategy_link.title
                result = StrategyService.apply_saved_strategy(data, strategy_link.id, db)
                if result is not None and not result.empty:
                    last = result.iloc[-1]
                    if last.get("Buy_Signal"):
                        signal = "BUY"
                    elif last.get("Sell_Signal"):
                        signal = "SELL"
                    else:
                        signal = "HOLD"

            response.append({
                "symbol": ticker,
                "price": price,
                "rsi": rsi,
                "ema_10": ema_10,
                "strategy": strategy_title,
                "signal": signal
            })

        return response

    except Exception as e:
        print(f"❌ Error in /stocks/overview: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)