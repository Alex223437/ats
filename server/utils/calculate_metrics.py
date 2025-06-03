import numpy as np


def calculate_equity_curve(df, trades_log, position, entry_price):
    equity_curve = []
    cumulative = 0

    for index, row in df.iterrows():
        trade_pnl = sum(
            t["pnl"] for t in trades_log
            if t["time"] == index and t["result"] in ("closed", "stop_loss", "take_profit")
        )
        cumulative += trade_pnl

        unrealized_pnl = 0
        if position == 'long':
            unrealized_pnl = row["Close"] - entry_price
        elif position == 'short':
            unrealized_pnl = entry_price - row["Close"]

        equity_curve.append({
            "date": index.isoformat(),
            "pnl": round(cumulative + unrealized_pnl, 4)
        })

    return equity_curve


def calculate_metrics(trades_log, equity_curve):
    trade_pnls = [t["pnl"] for t in trades_log if t["result"] in ("closed", "stop_loss", "take_profit")]
    pnl = sum(trade_pnls)
    win_rate = (np.array(trade_pnls) > 0).mean() * 100 if trade_pnls else 0
    sharpe_ratio = (
        (np.mean(trade_pnls) / np.std(trade_pnls)) * np.sqrt(252)
        if len(trade_pnls) > 1 and np.std(trade_pnls) > 0 else 0
    )

    peak = max_drawdown = 0
    for val in [pt["pnl"] for pt in equity_curve]:
        if val > peak:
            peak = val
        drawdown = peak - val
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    avg_pnl = np.mean(trade_pnls) if trade_pnls else 0

    return {
        "total_pnl": round(pnl, 2),
        "trades": len(trade_pnls),
        "win_rate": round(win_rate, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "max_drawdown": round(max_drawdown, 2),
        "average_pnl": round(avg_pnl, 2)
    }