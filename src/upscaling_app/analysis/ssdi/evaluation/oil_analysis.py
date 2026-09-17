import numpy as np
import pandas as pd

from upscaling_app import paths


def add_oil_metadata(
    results: pd.DataFrame,
) -> pd.DataFrame:
    experiments = pd.read_excel(
        paths.DATABASE_DIR / "experiments.xlsx",
        usecols=["experiment_id", "oil_id"],
    )

    return results.merge(
        experiments,
        on="experiment_id",
        how="left",
        validate="many_to_one",
    )


def calculate_oil_metrics(
    results: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for oil_id, group in results.groupby("oil_id"):
        d_exp = group["d50_exp"].to_numpy()
        d_pred = group["d50_pred"].to_numpy()

        rmse = np.sqrt(np.mean((d_exp - d_pred) ** 2))

        rows.append(
            {
                "oil_id": oil_id,
                "n": len(group),
                "mape": group["absolute_percentage_error"].mean(),
                "rmse": rmse,
                "mean_log_residual": group["log_residual"].mean(),
                "std_log_residual": group["log_residual"].std(),
                "outlier_count": int(group["is_outlier"].sum()),
            }
        )

    return pd.DataFrame(rows).sort_values("oil_id").reset_index(drop=True)
