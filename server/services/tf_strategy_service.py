from models.strategy import Strategy
from models.signal_log import SignalLog
from models.trade_log import TradeLog
from data.automation_data import fetch_intraday_alpaca
from services.alpaca_service import place_order, check_account, get_positions
from services.email_service import send_signal_notification, send_order_filled_notification, send_error_notification
from models.user_preferences import UserPreferences
from sqlalchemy.orm import Session
from ai_model.predictors.predict_conservative import predict_signals
import pandas as pd
from ai_model.strategies.conservative_executor import run_conservative_strategy
from datetime import datetime, timedelta
import numpy as np

def clean_debug_data(data: dict):
    def convert(val):
        if isinstance(val, (pd.Timestamp, datetime)):
            return val.isoformat()
        if isinstance(val, np.generic):
            return val.item()
        return val

    return {k: convert(v) for k, v in data.items()}

def run_tf_strategy_for_ticker(strategy: Strategy, ticker: str, user, db: Session):
    print(f"▶️ ML Strategy '{strategy.title}' checking {ticker}...")

    broker = next((b for b in user.brokers if b.is_connected), None)
    if not broker:
        print(f"❌ No connected broker for user {user.id}")
        return
    
    end = datetime.utcnow()
    start = end - timedelta(days=20)


    df = fetch_intraday_alpaca(
        symbol=ticker,
        timeframe=strategy.default_timeframe,
        start_date=start,
        end_date=end
    )
    if df is None or df.empty:
        print(f"⚠️ No data for {ticker}")
        return

    prediction = predict_signals(ticker, user.id, df)
    if prediction is None:
        print(f"⚠️ No prediction for {ticker}")
        return

    # 🔄 Получение открытых позиций
    positions = get_positions(broker)
    alpaca_pos = next((p for p in positions if p["symbol"] == ticker), None)

    current_position = None
    if alpaca_pos:
        qty = float(alpaca_pos["qty"])
        side = "long" if qty > 0 else "short"
        price = float(alpaca_pos["avg_entry_price"])
        current_position = {
            "type": side,
            "entry_price": price,
            "entry_time": pd.Timestamp.now()
        }

    df_result = pd.DataFrame([prediction])
    decision = run_conservative_strategy(df_result, current_position=current_position)
    if not decision or decision["action"] == "hold":
        print(f"⏸ HOLD: No action for {ticker}")
        return

    action = decision["action"]
    price = decision["price"]
    time = decision["time"]

    # === Определение объёма
    qty = None
    notional = None

    account = check_account(broker)
    if strategy.use_balance_percent:
        cash = float(account["cash"])
        amount = cash * (strategy.trade_amount / 100)
    else:
        amount = strategy.trade_amount

    qty = amount
    notional = amount if strategy.use_notional else None
    if strategy.use_notional:
        qty = None

    if action == "open":
        direction = decision["type"]
        debug_data=clean_debug_data(prediction)
        signal_log = SignalLog(
            user_id=user.id,
            strategy_id=strategy.id,
            ticker=ticker,
            action="buy" if direction == "long" else "sell",
            price=float(price),
            debug_data=debug_data,
            executed=False
        )
        db.add(signal_log)
        db.commit()

        prefs = db.query(UserPreferences).filter_by(user_id=user.id).first()
        if prefs and prefs.email_alerts_enabled and prefs.notify_on_signal:
            try:
                send_signal_notification(user.email, ticker, direction, price)
            except Exception as e:
                print(f"⚠️ Failed to send signal notification: {e}")

        

        trade = TradeLog(
            user_id=user.id,
            strategy_id=strategy.id,
            symbol=ticker,
            action="buy" if direction == "long" else "sell",
            price=float(price),
            quantity=int(notional or qty),
            is_order=True,
            status="pending"
        )
        db.add(trade)
        db.commit()

        if strategy.automation_mode == "FullAuto":
            try:
                order = place_order(
                    broker=broker,
                    symbol=ticker,
                    side="buy" if direction == "long" else "sell",
                    order_type=strategy.order_type,
                    time_in_force="day",
                    qty=qty,
                    notional=notional
                )
                trade.status = "matched"
                trade.is_order = False
                trade.broker_order_id = getattr(order, "id", None)
                signal_log.executed = True
                signal_log.result = "matched"
                db.commit()

                print(f"✅ Order placed: {ticker} at {price}")

                if prefs and prefs.email_alerts_enabled and prefs.notify_on_order_filled:
                    send_order_filled_notification(user.email, ticker, price, notional or qty)

            except Exception as e:
                trade.status = "rejected"
                signal_log.result = f"failed: {str(e)}"
                db.commit()
                print(f"❌ Order failed: {e}")

    elif action == "close":
      # Сначала ищем открытую позицию в базе
      last_open = (
          db.query(TradeLog)
          .filter(
              TradeLog.user_id == user.id,
              TradeLog.strategy_id == strategy.id,
              TradeLog.symbol == ticker,
              TradeLog.exit_time == None
          )
          .order_by(TradeLog.timestamp.desc())
          .first()
      )

      if last_open:
          # Закрываем существующую запись
          last_open.exit_price = price
          last_open.exit_time = time
          last_open.pnl = (price - last_open.price) if last_open.action == "buy" else (last_open.price - price)
          db.commit()
          print(f"✅ Closed tracked position in DB for {ticker} due to {decision.get('reason')}")
          prefs = db.query(UserPreferences).filter_by(user_id=user.id).first()
          if prefs and prefs.email_alerts_enabled and prefs.notify_on_order_filled:
              try:
                  send_order_filled_notification(user.email, ticker, price, qty)
              except Exception as e:
                  print(f"⚠️ Failed to send order filled notification: {e}")
      elif current_position:
          # Нет записи в БД, но есть брокерская позиция — логируем как новую закрывающую сделку
          direction = current_position["type"]
          entry_price = current_position["entry_price"]
          pnl = (price - entry_price) if direction == "long" else (entry_price - price)

          trade = TradeLog(
              user_id=user.id,
              strategy_id=strategy.id,
              symbol=ticker,
              action="sell" if direction == "long" else "buy",
              price=float(price),  # <-- тут
              quantity=int(qty),   # или float(), зависит от логики
              exit_price=float(price),
              exit_time=pd.Timestamp(time).to_pydatetime(),
              pnl=round(float(pnl), 4),
              is_order=False,
              status="matched"
          )
          db.add(trade)
          db.commit()
          print(f"✅ Closed broker-reported position on {ticker} due to {decision.get('reason')}")
          prefs = db.query(UserPreferences).filter_by(user_id=user.id).first()
          if prefs and prefs.email_alerts_enabled and prefs.notify_on_order_filled:
              try:
                  send_order_filled_notification(user.email, ticker, price, qty)
              except Exception as e:
                  print(f"⚠️ Failed to send order filled notification: {e}")
      else:
          print(f"❌ No position to close for {ticker} (neither in DB nor from broker)")
      if strategy.automation_mode == "FullAuto":
        try:
            order = place_order(
                broker=broker,
                symbol=ticker,
                side="sell" if direction == "long" else "buy",  # Закрываем позицию
                order_type=strategy.order_type,
                time_in_force="day",
                qty=qty,
                notional=notional
            )
            print(f"✅ Close order placed: {ticker} at {price}")
        except Exception as e:
            print(f"❌ Failed to place close order: {e}")
