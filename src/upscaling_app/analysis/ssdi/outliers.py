import pandas as pd


def mark_iqr_outliers(
    results: pd.DataFrame,
    factor: float = 1.5,
) -> pd.DataFrame:
    df = results.copy()

    q1 = df["log_residual"].quantile(0.25)
    q3 = df["log_residual"].quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr

    df["is_outlier"] = (df["log_residual"] < lower_bound) | (
        df["log_residual"] > upper_bound
    )

    return df
