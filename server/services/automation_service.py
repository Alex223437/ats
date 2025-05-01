from server.database import SessionLocal
from datetime import datetime
from server.models.strategy import Strategy
from server.models.user import User
from server.models.trade_log import TradeLog
from server.services.strategy_service import StrategyService
from server.services.broker_factory import get_alpaca_api
from server.data.market_data import MarketData
from sqlalchemy.orm import Session


def run_strategy(strategy: Strategy, db: Session):
    user = strategy.user
    api = get_alpaca_api(user)

    # Берем тикеры пользователя
    tickers = [stock.ticker for stock in user.stocks]
    for ticker in tickers:
        print(f"▶️ Запускаем стратегию '{strategy.title}' для {ticker}")
        
        # Получаем исторические данные
        data = MarketData.download_data(ticker, from_date="2024-01-01", to_date=str(datetime.today().date()))
        if data is None or data.empty:
            continue

        # Применяем стратегию
        result = StrategyService.apply_saved_strategy(data, strategy.id, db=db)
        if result is None or result.empty:
            continue

        last_row = result.iloc[-1]
        print(last_row)

        # Покупка
        if last_row.get("Buy_Signal"):
            _log_and_trade(api, db, user, ticker, "buy", strategy)

        # Продажа
        elif last_row.get("Sell_Signal"):
            _log_and_trade(api, db, user, ticker, "sell", strategy)
        
        else:
            print('neither buy or sell')


def _log_and_trade(api, db, user: User, ticker: str, action: str, strategy: Strategy):
    # Создаем лог
    log = TradeLog(
        user_id=user.id,
        strategy_id=strategy.id,
        ticker=ticker,
        action=action,
        price=0,  # можно расширить получением текущей цены
        status="executed"
    )
    db.add(log)
    db.commit()

    print(f"📈 Выполнено действие: {action.upper()} {ticker} по стратегии {strategy.title}")

    # Автоматическая торговля (если выбран режим Auto)
    if strategy.automation_mode == "Automatic":
        try:
            api.submit_order(
                symbol=ticker,
                qty=1,  # временно фиксировано
                side=action,
                type="market",
                time_in_force="gtc"
            )
            print(f"✅ Отправлен рыночный ордер на {action.upper()} {ticker}")
        except Exception as e:
            print(f"❌ Ошибка при отправке ордера: {e}")

def check_and_run_strategies():
    print("⏱ Проверяем активные стратегии...")
    db = SessionLocal()
    try:
        active = db.query(Strategy).filter(Strategy.is_enabled == True).all()
        for strategy in active:
            run_strategy(strategy, db)
    except Exception as e:
        print(f"❌ Ошибка при запуске стратегии: {e}")
    finally:
        db.close()