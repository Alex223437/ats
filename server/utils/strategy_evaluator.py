import pandas as pd
import numpy as np

def eval_expr(expr: str, df: pd.DataFrame) -> pd.Series:
    """
    Evaluates a boolean expression string against a pandas DataFrame.
    
    Example: "RSI < 30 and EMA_10 > Close"
    """
    # Поддержка логических операторов
    allowed_names = {
        **{col: df[col] for col in df.columns},
        "and": np.logical_and,
        "or": np.logical_or,
        "not": np.logical_not,
        "True": True,
        "False": False,
    }

    try:
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        if isinstance(result, pd.Series):
            return result.fillna(False)
        else:
            return pd.Series([False] * len(df))
    except Exception as e:
        print(f"❌ Ошибка в eval_expr: {e}")
        return pd.Series([False] * len(df))