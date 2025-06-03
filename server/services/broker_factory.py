import alpaca_trade_api as tradeapi
from models.broker import UserBroker

def get_alpaca_api_from_broker(broker: UserBroker):
    if not broker.api_key or not broker.api_secret or not broker.base_url:
        raise ValueError("Alpaca credentials are incomplete.")
    
    return tradeapi.REST(
        key_id=broker.api_key,
        secret_key=broker.api_secret,
        base_url=broker.base_url,
        api_version='v2'
    )

def get_api_client(broker: UserBroker):
    if broker.broker.lower() == "alpaca":
        return get_alpaca_api_from_broker(broker)
    raise NotImplementedError(f"Broker '{broker.broker}' not supported.")