import pandas as pd
from data.market_data import MarketData
from services.strategy_service import StrategyService

class DataAnalysisService:
    @staticmethod
    def get_strategy_result(ticker: str, strategy_id: str | None = None) -> pd.DataFrame:
        data = MarketData.download_data(ticker)
        if data is None or data.empty:
            raise ValueError(f"Could not fetch data for {ticker}")

        if isinstance(strategy_id, int) or (isinstance(strategy_id, str) and strategy_id.isdigit()):
            return StrategyService.apply_saved_strategy(data, int(strategy_id))
        else:
            return StrategyService.apply_moving_average_strategy(data)