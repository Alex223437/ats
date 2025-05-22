from database import SessionLocal
from datetime import datetime, timedelta
from models.strategy import Strategy
from models.signal_log import SignalLog
from models.trade_log import TradeLog
from models.strategy_ticker import StrategyTicker
from services.strategy_service import StrategyService
from services.broker_factory import get_alpaca_api
from data.automation_data import fetch_intraday_alpaca
from services.alpaca_service import place_order
from sqlalchemy.orm import Session
import hashlib
import json

def get_debug_hash(data: dict) -> str:
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

def parse_check_frequency(freq: str) -> timedelta:
    mapping = {
        "1 Minute": timedelta(minutes=1),
        "5 Minutes": timedelta(minutes=5),
        "15 Minutes": timedelta(minutes=15),
        "1 Hour": timedelta(hours=1),
        "1 Day": timedelta(days=1),
    }
    return mapping.get(freq, timedelta(hours=1))


def run_strategy_for_ticker(strategy: Strategy, ticker: str, user, db: Session):
    print(f"▶️ Strategy '{strategy.title}' checking {ticker}...")

    # используем Alpaca вместо stockdata.org
    df = fetch_intraday_alpaca(
        symbol=ticker,
        timeframe="5Min",
        minutes_back=60
    )

    if df is None or df.empty:
        print(f"⚠️ No data for {ticker}")
        return

    result = StrategyService.apply_saved_strategy(df, strategy.id, db)
    if result is None or result.empty:
        print(f"⚠️ Strategy returned empty for {ticker}")
        return

    signal = result.iloc[-1]
    action = None
    if signal.get("Buy_Signal"):
        action = "buy"
    elif signal.get("Sell_Signal"):
        action = "sell"

    if action:
        price = signal.get("Close", 0.0)
        debug_dict = signal.to_dict()
        new_hash = get_debug_hash(debug_dict)
        last_signal = (
            db.query(SignalLog)
            .filter(
                SignalLog.strategy_id == strategy.id,
                SignalLog.ticker == ticker
            )
            .order_by(SignalLog.created_at.desc())
            .first()
        )

        if last_signal and get_debug_hash(last_signal.debug_data) == new_hash:
            print(f"🛑 Duplicate signal for {ticker} skipped.")
            return
        
        new_signal = SignalLog(
            user_id=user.id,
            strategy_id=strategy.id,
            ticker=ticker,
            action=action,
            price=price,
            debug_data=debug_dict,
            executed=False
        )
        db.add(new_signal)
        db.commit()
        print(f"📝 Signal logged: {action.upper()} {ticker}")

        trade = TradeLog(
            user_id=user.id,
            strategy_id=strategy.id,
            symbol=ticker,
            action=action,
            price=price,
            quantity=strategy.trade_amount,
            is_order=True,
            status="pending"
        )
        db.add(trade)
        db.commit()

        if strategy.auto_trade:
            try:
                # 🧠 Отправка ордера через place_order
                order = place_order(
                    user=user,
                    symbol=ticker,
                    qty=strategy.trade_amount,
                    side=action,
                    order_type=strategy.order_type,
                    time_in_force="gtc"
                )

                # Обработка ошибок, если place_order вернул словарь с ошибкой
                if isinstance(order, dict) and order.get("status") == "error":
                    raise Exception(order.get("message", "Unknown error"))

                broker_order_id = getattr(order, "id", None)

                trade.status = "matched"
                trade.is_order = False
                trade.broker_order_id = broker_order_id

                new_signal.executed = True
                new_signal.result = "matched"

                db.commit()
                print(f"✅ Order placed: {action.upper()} {ticker} x{strategy.trade_amount}")

            except Exception as e:
                trade.status = "rejected"
                new_signal.result = f"failed: {str(e)}"
                db.commit()
                print(f"❌ Order failed: {e}")
    else:
        print(f"⏹ No signal for {ticker}")


def check_and_run_strategies():
    print("🧠 Running strategy engine...")
    db = SessionLocal()
    now = datetime.utcnow()

    try:
        strategies = db.query(Strategy).filter(Strategy.is_enabled == True).all()

        for strategy in strategies:
            interval = parse_check_frequency(strategy.market_check_frequency)
            if strategy.last_checked and (now - strategy.last_checked) < interval:
                print(f"⏩ Skipping '{strategy.title}' (too early)")
                continue

            user = strategy.user
            for link in strategy.tickers:
                ticker = link.user_stock.ticker
                run_strategy_for_ticker(strategy, ticker, user, db)

            strategy.last_checked = now
            db.commit()

    finally:
        db.close()