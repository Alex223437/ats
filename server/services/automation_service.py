from database import SessionLocal
from datetime import datetime, timedelta
from models.strategy import Strategy
from models.signal_log import SignalLog
from models.trade_log import TradeLog
from models.strategy_ticker import StrategyTicker
from services.strategy_service import StrategyService
from data.automation_data import fetch_intraday_alpaca
from data.alpaca_data import fetch_history_alpaca
from services.alpaca_service import place_order, check_account, get_positions
from services.email_service import send_signal_notification, send_order_filled_notification, send_error_notification
from models.user_preferences import UserPreferences
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

def get_tp_sl_prices(price, action, strategy):
    tp = None
    sl = None

    if strategy.take_profit:
        tp_val = strategy.take_profit / 100 if strategy.sl_tp_is_percent else strategy.take_profit
        if action == "buy":
            tp = round(price * (1 + tp_val), 2) if strategy.sl_tp_is_percent else round(price + tp_val, 2)
        else:  # sell
            tp = round(price * (1 - tp_val), 2) if strategy.sl_tp_is_percent else round(price - tp_val, 2)

    if strategy.stop_loss:
        sl_val = strategy.stop_loss / 100 if strategy.sl_tp_is_percent else strategy.stop_loss
        if action == "buy":
            sl = round(price * (1 - sl_val), 2) if strategy.sl_tp_is_percent else round(price - sl_val, 2)
        else:  # sell
            sl = round(price * (1 + sl_val), 2) if strategy.sl_tp_is_percent else round(price + sl_val, 2)

    return tp, sl

def run_strategy_for_ticker(strategy: Strategy, ticker: str, user, db: Session):
    print(f"▶️ Strategy '{strategy.title}' checking {ticker}...")

    broker = next((b for b in user.brokers if b.is_connected), None)
    if not broker:
        print(f"❌ No connected broker for user {user.id}")
        return


    # df = fetch_history_alpaca(symbol=ticker, start=start, end=end, timeframe=strategy.default_timeframe)
    df = fetch_intraday_alpaca(symbol=ticker, timeframe=strategy.default_timeframe, minutes_back=240)
    if df is None or df.empty:
        print(f"⚠️ No data for {ticker}")
        return

    result = StrategyService.apply_saved_strategy(df, strategy.id, db)
    if result is None or result.empty:
        print(f"⚠️ Strategy returned empty for {ticker}")
        return

    recent = result.tail(strategy.confirmation_candles or 1)
    buy_confirmed = all(row.get("Buy_Signal") for _, row in recent.iterrows())
    sell_confirmed = all(row.get("Sell_Signal") for _, row in recent.iterrows())
    action = "buy" if buy_confirmed else "sell" if sell_confirmed else None

    if not action:
        print(f"⏹ No confirmed signal for {ticker}")
        return

    price = float(recent.iloc[-1].get("Close", 0.0))
    debug_data = recent.iloc[-1].to_dict()
    signal_hash = get_debug_hash(debug_data)

    last_signal = (
        db.query(SignalLog)
        .filter(SignalLog.strategy_id == strategy.id, SignalLog.ticker == ticker)
        .order_by(SignalLog.created_at.desc())
        .first()
    )
    if last_signal and get_debug_hash(last_signal.debug_data) == signal_hash:
        print(f"🛑 Duplicate signal for {ticker} skipped.")
        return

    new_signal = SignalLog(
        user_id=user.id,
        strategy_id=strategy.id,
        ticker=ticker,
        action=action,
        price=price,
        debug_data=debug_data,
        executed=False
    )
    db.add(new_signal)
    db.commit()

    prefs = db.query(UserPreferences).filter_by(user_id=user.id).first()
    if prefs and prefs.email_alerts_enabled and prefs.notify_on_signal:
        try:
            send_signal_notification(user.email, ticker, action, price)
        except Exception as e:
            print(f"⚠️ Failed to send signal notification: {e}")

    qty = None
    notional = None
    if strategy.use_balance_percent:
        account = check_account(broker)
        cash = float(account["cash"])
        amount = cash * (strategy.trade_amount / 100)
    else:
        amount = strategy.trade_amount

    qty = round(amount / price, 2)
    notional = amount if strategy.use_notional else None
    if strategy.use_notional:
        qty = None

    trade = TradeLog(
        user_id=user.id,
        strategy_id=strategy.id,
        symbol=ticker,
        action=action,
        price=price,
        quantity=notional or qty,
        is_order=True,
        status="pending"
    )
    db.add(trade)
    db.commit()

    print(f"📈 {action.upper()} signal for {ticker} at ${price:.2f} | Qty: {qty} | Notional: ${notional}")

    if strategy.automation_mode == "FullAuto":
        order_type = strategy.order_type
        time_in_force = "day"

        if notional:
            if order_type != "market":
                print("❌ Notional only valid with market orders")
                trade.status = "rejected"
                new_signal.result = "failed: notional invalid with non-market"
                db.commit()
                return
            time_in_force = "day"

        # 🛡 Защита: нельзя использовать SL/TP при notional или percent
        if (strategy.take_profit or strategy.stop_loss) and (strategy.use_notional or strategy.use_balance_percent):
            print("❌ TP/SL поддерживаются только при использовании фиксированного qty")
            trade.status = "rejected"
            new_signal.result = "failed: TP/SL not allowed with notional or balance percent"
            db.commit()
            return

        # 🛡 Защита: нельзя шортить fractional, если нет позиции
        if action == "sell" and (strategy.use_notional or strategy.use_balance_percent):
            print("❌ Short with notional or balance % запрещен")
            trade.status = "rejected"
            new_signal.result = "failed: short not allowed with notional or percent"
            db.commit()
            return

        if action == "sell" and qty is not None and not qty.is_integer():
            positions = get_positions(broker)
            current = next((p for p in positions if p["symbol"] == ticker), None)
            has_long_position = current and float(current["qty"]) >= qty
            if not has_long_position:
                print(f"❌ Cannot short fractional shares for {ticker}: qty={qty}")
                trade.status = "rejected"
                new_signal.result = "failed: fractional short not allowed"
                db.commit()
                return

        take_profit, stop_loss = get_tp_sl_prices(price, action, strategy)
        order_class = "bracket" if take_profit or stop_loss else None

        # 🛡 Защита: bracket не поддерживает fractional qty
        if order_class == "bracket" and qty is not None and not qty.is_integer():
            print(f"❌ Bracket-ордера не поддерживают fractional qty: {qty}")
            trade.status = "rejected"
            new_signal.result = "failed: fractional qty not allowed for bracket"
            db.commit()
            return

        order_kwargs = {
            "broker": broker,
            "symbol": ticker,
            "side": action,
            "order_type": order_type,
            "order_class": order_class,
            "time_in_force": time_in_force,
            "qty": qty,
            "notional": notional,
            "take_profit": take_profit,
            "stop_loss": stop_loss
        }

        clean_order_kwargs = {k: v for k, v in order_kwargs.items() if v is not None}

        try:
            order = place_order(**clean_order_kwargs)

            trade.status = "matched"
            trade.is_order = False
            trade.broker_order_id = getattr(order, "id", None)
            new_signal.executed = True
            new_signal.result = "matched"
            db.commit()

            print(f"✅ Order placed: {action.upper()} {ticker}")

            if prefs and prefs.email_alerts_enabled and prefs.notify_on_order_filled:
                send_order_filled_notification(user.email, ticker, price, notional or qty)

        except Exception as e:
            error_msg = str(e)
            trade.status = "rejected"
            new_signal.result = f"failed: {error_msg}"
            db.commit()

            print(f"❌ Order failed: {error_msg}")
            if prefs and prefs.email_alerts_enabled and prefs.notify_on_error:
                send_error_notification(user.email, error_msg)

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