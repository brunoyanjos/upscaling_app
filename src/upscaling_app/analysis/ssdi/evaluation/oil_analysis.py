import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.ssdi.metrics import (
    calculate_global_metrics,
)


def add_oil_metadata(
    results: pd.DataFrame,
) -> pd.DataFrame:
    experiments = pd.read_excel(
        paths.EXPERIMENTS_DATABASE,
        usecols=[
            "experiment_id",
            "oil_id",
        ],
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
        metrics = calculate_global_metrics(group)

        rows.append(
            {
                "oil_id": oil_id,
                "n": len(group),
                "log_mse": metrics["log_mse"],
                "r2": metrics["r2"],
                "rmse": metrics["rmse"],
                "mape": metrics["mape"],
                "mean_log_residual": float(group["log_residual"].mean()),
                "std_log_residual": float(group["log_residual"].std()),
                "outlier_count": int(group["is_outlier"].sum()),
            }
        )

    return pd.DataFrame(rows).sort_values("oil_id").reset_index(drop=True)
