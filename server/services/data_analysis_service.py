import pandas as pd
from server.data.market_data import MarketData
from server.services.strategy_service import StrategyService

class DataAnalysisService:
    @staticmethod
    def get_strategy_result(ticker: str, strategy_id: str | None = None) -> pd.DataFrame:
        data = MarketData.download_data(ticker, from_date="2024-01-01", to_date="2025-03-27")
        if data is None or data.empty:
            raise ValueError(f"Could not fetch data for {ticker}")

        if strategy_id == "ai":
            return StrategyService.apply_ai_prediction(data)
        elif isinstance(strategy_id, int) or (isinstance(strategy_id, str) and strategy_id.isdigit()):
            return StrategyService.apply_saved_strategy(data, int(strategy_id))
        else:
            return StrategyService.apply_moving_average_strategy(data)