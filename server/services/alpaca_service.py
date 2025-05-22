import alpaca_trade_api as tradeapi
from models.user import User

def get_alpaca_api(user: User):
    """Инициализация клиента Alpaca по ключам пользователя"""
    return tradeapi.REST(
        user.alpaca_api_key,
        user.alpaca_api_secret,
        user.alpaca_base_url,
        api_version='v2'
    )

def check_account(user: User):
    api = get_alpaca_api(user)
    account = api.get_account()
    return {"cash": account.cash, "status": account.status}

def place_order(user: User, symbol, qty, side, order_type, time_in_force,
                limit_price=None, stop_price=None,
                trail_price=None, trail_percent=None):
    api = get_alpaca_api(user)
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=order_type,
            time_in_force=time_in_force,
            limit_price=limit_price,
            stop_price=stop_price,
            trail_price=trail_price,
            trail_percent=trail_percent
        )
        return order  # Возвращаем сам объект order (или словарь если хочешь)
    except Exception as e:
        raise RuntimeError(f"Alpaca order error: {str(e)}")
    
def get_positions(user: User):
    api = get_alpaca_api(user)
    positions = api.list_positions()
    return [
        {
            "symbol": pos.symbol,
            "qty": float(pos.qty),
            "avg_entry_price": float(pos.avg_entry_price),
            "current_price": float(pos.current_price),
            "market_value": float(pos.market_value),
            "unrealized_pl": float(pos.unrealized_pl),
            "unrealized_plpc": float(pos.unrealized_plpc),
        }
        for pos in positions
    ]

def get_open_orders(user: User):
    api = get_alpaca_api(user)
    orders = api.list_orders(status="open")
    return [
        {
            "id": order.id,
            "symbol": order.symbol,
            "order_type": order.order_type,
            "side": order.side,
            "qty": order.qty,
            "filled_qty": order.filled_qty,
            "avg_fill_price": getattr(order, "avg_fill_price", "N/A"),
            "status": order.status,
            "submitted_at": order.submitted_at,
            "filled_at": getattr(order, "filled_at", "N/A"),
        }
        for order in orders
    ]

def cancel_order(user: User, order_id):
    api = get_alpaca_api(user)
    try:
        api.cancel_order(order_id)
        return {"status": "success", "message": f"Order {order_id} canceled"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def close_position(user: User, symbol):
    api = get_alpaca_api(user)
    try:
        api.close_position(symbol)
        return {"status": "success", "message": f"Position {symbol} closed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}