from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import matplotlib.pyplot as plt
import io
import base64
from server.services.ai_service import predict_signals
from server.data.market_data import MarketData

ai_router = APIRouter()

@ai_router.get("/ai/predict/{ticker}")
async def get_ai_prediction(ticker: str):
    """Прогноз сигналов для акции"""
    data = MarketData.download_data(ticker)
    if data is None:
        return {"error": "Не удалось загрузить данные"}

    prediction = predict_signals(data)
    return prediction[['Close', 'Buy_Prediction', 'Sell_Prediction']].fillna(0).to_dict(orient='records')

@ai_router.get("/ai/visualize/{ticker}", response_class=HTMLResponse)
async def visualize_ai_prediction(ticker: str):
    """Визуализирует предсказания AI"""
    data = MarketData.download_data(ticker)
    if data is None:
        return "<h1>Ошибка: не удалось загрузить данные</h1>"

    prediction = predict_signals(data)

    # Рисуем график
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(prediction.index, prediction['Close'], label='Close Price', color='blue')

    # Buy точки
    buy_signals = prediction[prediction['Buy_Prediction'] == 1]
    ax.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', label='Buy Signal', s=100)

    # Sell точки
    sell_signals = prediction[prediction['Sell_Prediction'] == 1]
    ax.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', label='Sell Signal', s=100)

    ax.legend()
    ax.set_title(f"AI Predictions for {ticker}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")

    # Конвертируем график в изображение base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    img_tag = f'<img src="data:image/png;base64,{img_base64}" />'

    return f"<h1>График предсказаний AI ({ticker})</h1>{img_tag}"