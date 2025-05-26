from models.broker import UserBroker
from services.broker_factory import get_api_client
import json


def check_account(broker: UserBroker):
    api = get_api_client(broker)
    account = api.get_account()
    return {"cash": account.cash, "status": account.status}


def place_order(
    broker: UserBroker,
    symbol: str,
    qty: float = None,
    notional: float = None,
    side: str = "buy",
    order_type: str = "market",  # ← это type
    order_class: str = "",       # ← это order_class: "" or "bracket"
    time_in_force: str = "day",
    limit_price: float = None,
    stop_price: float = None,
    trail_price: float = None,
    trail_percent: float = None,
    take_profit: float = None,
    stop_loss: float = None
):
    api = get_api_client(broker)

    # ✅ Валидация
    if notional and qty:
        raise ValueError("You cannot specify both 'qty' and 'notional'")

    if not notional and not qty:
        raise ValueError("You must specify either 'qty' or 'notional'")

    if notional and (order_type != "market" or time_in_force != "day"):
        raise ValueError("Notional orders are only allowed with order_type='market' and time_in_force='day'")

    # 📦 Аргументы запроса
    order_args = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "time_in_force": time_in_force,
    }

    if order_class == "bracket":
        if qty is None:
            raise ValueError("Bracket orders require 'qty'")
        order_args["qty"] = qty
        order_args["order_class"] = "bracket"

        if take_profit:
            order_args["take_profit"] = {"limit_price": round(take_profit, 2)}
        if stop_loss:
            order_args["stop_loss"] = {"stop_price": round(stop_loss, 2)}

    else:
        if notional is not None:
            order_args["notional"] = round(notional, 2)
        else:
            order_args["qty"] = qty

        if limit_price is not None:
            order_args["limit_price"] = round(limit_price, 2)
        if stop_price is not None:
            order_args["stop_price"] = round(stop_price, 2)
        if trail_price is not None:
            order_args["trail_price"] = round(trail_price, 2)
        if trail_percent is not None:
            order_args["trail_percent"] = round(trail_percent, 2)

    print(f"📤 Alpaca Order Payload:\n{json.dumps(order_args, indent=2)}")

    try:
        return api.submit_order(**order_args)
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