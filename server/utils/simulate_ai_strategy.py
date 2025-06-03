import pandas as pd
from ai_model.predictors.predict_signals_batch import predict_signals_batch
from ai_model.strategies.execute_ml_tf import execute_conservative_strategy


def simulate_ai_strategy(ticker: str, user_id: int, df: pd.DataFrame) -> tuple[list[dict], list[dict], str | None, float | None]:
    """
    Simulates a trading strategy using AI-generated signals.
    """
    df = df.copy()

    try:
        signal_df = predict_signals_batch(ticker=ticker, user_id=user_id, df=df)
        if signal_df.empty:
            raise ValueError("AI signals dataframe is empty")
    except Exception as e:
        print(f"Failed to generate AI predictions: {e}")
        raise ValueError("Failed to generate AI predictions") from e

    df = df.merge(signal_df, left_index=True, right_index=True, how="left")
    df["signal"] = df["signal"].fillna("hold")
    df["confidence"] = df["confidence"].fillna(0.0)

    trades_log, equity_curve, position, entry_price = execute_conservative_strategy(df)

    return trades_log, equity_curve, position, entry_price