import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score


def add_point_metrics(results: pd.DataFrame) -> pd.DataFrame:
    df = results.copy()

    if (df["d50_exp"] <= 0).any() or (df["d50_pred"] <= 0).any():
        raise ValueError("d50 values must be positive.")

    df["absolute_percentage_error"] = (
        np.abs(df["d50_exp"] - df["d50_pred"]) / df["d50_exp"] * 100.0
    )

    df["log_residual"] = np.log(df["d50_exp"]) - np.log(df["d50_pred"])

    return df


def calculate_global_metrics(
    results: pd.DataFrame,
) -> dict[str, float]:
    d_exp = results["d50_exp"].to_numpy()
    d_pred = results["d50_pred"].to_numpy()

    return {
        "r2": float(r2_score(d_exp, d_pred)),
        "rmse": float(
            np.sqrt(
                mean_squared_error(
                    d_exp,
                    d_pred,
                )
            )
        ),
        "mape": float(results["absolute_percentage_error"].mean()),
    }
