from models.broker import UserBroker
from services.broker_factory import get_api_client


def check_account(broker: UserBroker):
    api = get_api_client(broker)
    account = api.get_account()
    return {"cash": account.cash, "status": account.status}


def place_order(
    broker: UserBroker,
    symbol: str,
    qty: int,
    side: str,
    order_type: str,
    time_in_force: str,
    limit_price: float = None,
    stop_price: float = None,
    trail_price: float = None,
    trail_percent: float = None
):
    api = get_api_client(broker)
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
            trail_percent=trail_percent,
        )
        return order
    except Exception as e:
        raise RuntimeError(f"Alpaca order error: {str(e)}")


def get_positions(broker: UserBroker):
    api = get_api_client(broker)
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


def get_open_orders(broker: UserBroker):
    api = get_api_client(broker)
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


def cancel_order(broker: UserBroker, order_id: str):
    api = get_api_client(broker)
    try:
        api.cancel_order(order_id)
        return {"status": "success", "message": f"Order {order_id} canceled"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def close_position(broker: UserBroker, symbol: str):
    api = get_api_client(broker)
    try:
        api.close_position(symbol)
        return {"status": "success", "message": f"Position {symbol} closed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}