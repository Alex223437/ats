import alpaca_trade_api as tradeapi

def get_alpaca_api(user):
  if not user.alpaca_api_key or not user.alpaca_api_secret or not user.alpaca_base_url:
    raise ValueError("The user does not have a valid Alpaca API key, secret, or base URL.")
  
  return tradeapi.REST(
    key_id=user.alpaca_api_key,
    secret_key=user.alpaca_api_secret,
    base_url=user.alpaca_base_url,
    api_version='v2'
  )