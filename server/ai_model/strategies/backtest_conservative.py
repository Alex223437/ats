import pandas as pd
import matplotlib.pyplot as plt

# === Параметры стратегии
TAKE_PROFIT = 0.01  # +1%
STOP_LOSS = -0.005  # -0.5%
ALLOWED_HOURS = range(15, 22)  # американская сессия: 15:00–21:59 UTC
MIN_CONFIDENCE = 0.4

# === Загрузка данных с сигналами
df = pd.read_csv("cnn_lstm_reg_signals.csv", parse_dates=["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# === Инициализация
equity = [1.0]
position = None
entry_price = 0
entry_time = None
trades = []

# === Фильтрация сигналов по уверенности и времени
df = df[df["confidence"] >= MIN_CONFIDENCE]
df = df[df["timestamp"].dt.hour.isin(ALLOWED_HOURS)]

# === Обработка сигналов
for i, row in df.iterrows():
    signal = row["signal"]
    price = row["real_close"]
    time = row["timestamp"]
    confidence = row.get("confidence", 1.0)  # по умолчанию 1.0, если нет

    if position is None:
        if signal == "buy":
            position = "long"
            entry_price = price
            entry_time = time
        elif signal == "sell":
            position = "short"
            entry_price = price
            entry_time = time
    else:
        if (position == "long" and signal == "sell") or (position == "short" and signal == "buy"):
            exit_reason = "opposite_signal"
            # Закрытие позиции
            pnl = (price - entry_price) / entry_price if position == "long" else (entry_price - price) / entry_price
            trades.append({
                "entry_time": entry_time,
                "exit_time": time,
                "entry_price": entry_price,
                "exit_price": price,
                "type": position,
                "profit": pnl,
                "exit_reason": exit_reason
            })
            equity.append(equity[-1] * (1 + pnl))
            position = None
            entry_price = 0
            entry_time = None
        else:
            equity.append(equity[-1])
    # Логика выхода по TP/SL
    if position:
        if position == "long":
            change = (price - entry_price) / entry_price
        elif position == "short":
            change = (entry_price - price) / entry_price

        if change >= TAKE_PROFIT or change <= STOP_LOSS:
            exit_reason = "take_profit" if change >= TAKE_PROFIT else "stop_loss"
            pnl = change
            trades.append({
                "entry_time": entry_time,
                "exit_time": time,
                "entry_price": entry_price,
                "exit_price": price,
                "type": position,
                "profit": pnl,
                "exit_reason": exit_reason
            })
            equity.append(equity[-1] * (1 + pnl))
            position = None
            entry_price = 0
            entry_time = None
            continue

    if position is None:
        equity[-1] = equity[-1]  # no-op
    elif position == "long":
        if len(equity) >= 2:
            equity[-1] = equity[-2] * (1 + (price - entry_price) / entry_price)
        else:
            equity[-1] = equity[-1] * (1 + (price - entry_price) / entry_price)
    elif position == "short":
        if len(equity) >= 2:
            equity[-1] = equity[-2] * (1 + (entry_price - price) / entry_price)
        else:
            equity[-1] = equity[-1] * (1 + (entry_price - price) / entry_price)

# === Вывод результатов
trades_df = pd.DataFrame(trades)
if trades_df.empty:
    print("⚠️ Нет совершённых сделок. Проверь сигналы.")
    exit()

if "profit" in trades_df.columns:
    win_trades = trades_df[trades_df["profit"] > 0]
else:
    print("❌ Колонка 'profit' отсутствует в таблице сделок.")
    exit()

print(f"📈 Total trades: {len(trades_df)}")
print(f"✅ Win rate: {len(win_trades) / len(trades_df) * 100:.2f}%")
print(f"📊 Avg profit per trade: {trades_df['profit'].mean() * 100:.2f}%")
print(f"📉 Max drawdown: {100 * (1 - min(equity) / max(equity)):.2f}%")

import numpy as np

returns = pd.Series(equity).pct_change().dropna()
sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252 * 6.5)  # 252 торговых дня * 6.5 часов (в часах)
total_return = equity[-1] - 1
start_date = df["timestamp"].min()
end_date = df["timestamp"].max()
days = (end_date - start_date).days
if days > 0:
    annualized_return = (1 + total_return) ** (365 / days) - 1
else:
    annualized_return = 0

print(f"🗓️ Backtest period: {start_date.date()} — {end_date.date()} ({days} days)")
print(f"⏱️ Bars (returns): {len(returns)}")
print(f"📉 Mean return: {returns.mean():.5f}, StdDev: {returns.std():.5f}")
print(f"📈 Sharpe Ratio: {sharpe_ratio:.2f}")
print(f"📈 Total Return: {total_return * 100:.2f}%")
print(f"📈 Annualized Return: {annualized_return * 100:.2f}%")

# === График Equity Curve
plt.figure(figsize=(12, 6))
plt.plot(df["timestamp"][:len(equity)], equity)
plt.title("📈 Equity Curve")
plt.xlabel("Time")
plt.ylabel("Equity")
plt.grid(True)
plt.tight_layout()
plt.show()

# === Сохранение сделок
trades_df[["entry_time", "exit_time", "entry_price", "exit_price", "type", "profit", "exit_reason"]].to_csv("conservative_backtest_trades.csv", index=False)
print("💾 Сделки сохранены в conservative_backtest_trades.csv")