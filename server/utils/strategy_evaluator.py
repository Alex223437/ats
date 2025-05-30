import re
import pandas as pd
import numpy as np

def eval_expr(expr: str, df: pd.DataFrame) -> pd.Series:
    """
    Evaluates a boolean expression string against a pandas DataFrame.
    Automatically converts 'and', 'or', 'not' into bitwise ops and adds parentheses to avoid precedence issues.
    """

    expr = re.sub(r'([a-zA-Z0-9_]+ *[<>=!]=? *[^&|() ]+)', r'(\1)', expr)
    expr = expr.replace(" and ", " & ").replace(" or ", " | ").replace(" not ", " ~ ")

    allowed_names = {col: df[col] for col in df.columns}
    allowed_names.update({"True": True, "False": False})

    try:
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        if isinstance(result, pd.Series):
            return result.fillna(False)
        return pd.Series([False] * len(df))
    except Exception as e:
        print(f"Error in eval_expr: {e}")
        print(f"Error: {expr}")
        return pd.Series([False] * len(df))