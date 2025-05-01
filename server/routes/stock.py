from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import asyncio
from services.data_analysis_service import DataAnalysisService
from data.market_data import MarketData


stock_router = APIRouter()

@stock_router.get("/api/data/{ticker}")
async def get_stock_data(ticker: str, strategy_id: str | None = Query(None)):
    try:
        result = await asyncio.to_thread(DataAnalysisService.get_strategy_result, ticker, strategy_id)
        
        print(f"✅ Стратегия успешно применена, {len(result)} записей")

        result = result.reset_index()
        result['Date'] = result['Date'].dt.strftime('%Y-%m-%d')
        result['Buy_Signal'] = result.get('Buy_Signal', False).astype(bool)
        result['Sell_Signal'] = result.get('Sell_Signal', False).astype(bool)

        response_columns = ['Date', 'Close', 'Buy_Signal', 'Sell_Signal']
        if 'SMA_Short' in result.columns:
            response_columns.append('SMA_Short')
        if 'SMA_Long' in result.columns:
            response_columns.append('SMA_Long')

        response = result[response_columns].to_dict(orient='records')
        return JSONResponse(content={"data": response})
    
    except HTTPException as http_error:
        return JSONResponse(content={"error": http_error.detail}, status_code=http_error.status_code)

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

        latest = df.iloc[-1]  # Последняя строка

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
        print(f"❌ Ошибка индикаторов: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)