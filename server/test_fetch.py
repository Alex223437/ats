from data.automation_data import fetch_intraday_alpaca
from datetime import datetime, timedelta

# Задаем даты
start = datetime(2025, 4, 1)
end = datetime(2025, 4, 20)

# Считаем интервал в минутах
minutes_back = int((end - start).total_seconds() // 60)

# Вызываем Alpaca
df = fetch_intraday_alpaca(
    symbol="AAPL",
    timeframe="1Hour",
    minutes_back=minutes_back
)

# Выводим результат
print(f"\n📊 Получено {len(df)} строк:\n")
print(df.head(10))
print(df.tail(10))
print(df.index.min(), "→", df.index.max())