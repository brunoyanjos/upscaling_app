import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.ssdi.metrics import (
    add_point_metrics,
    calculate_global_metrics,
)
from upscaling_app.analysis.ssdi.outliers import (
    mark_iqr_outliers,
)

METADATA_COLUMNS = [
    "experiment_id",
    "oil_id",
    "dispersion_tag",
    "nozzle_diameter",
    "has_gas",
]


def prepare_performance_results(
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    metadata = pd.read_excel(
        paths.EXPERIMENTS_DATABASE,
        usecols=METADATA_COLUMNS,
    )

    if metadata["experiment_id"].duplicated().any():
        raise ValueError(
            "Duplicate experiment_id values found in experiments database."
        )

    results = predictions.merge(
        metadata,
        on="experiment_id",
        how="left",
        validate="one_to_one",
    )

    if results["oil_id"].isna().any():
        raise ValueError(
            "Some SSDI predictions could not be linked " "to experimental metadata."
        )

    results = add_point_metrics(
        results,
    )

    results = mark_iqr_outliers(
        results,
    )

    return results


def calculate_oil_metrics(
    results: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for oil_id, group in results.groupby(
        "oil_id",
        sort=True,
    ):
        metrics = calculate_global_metrics(
            group,
        )

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

    return pd.DataFrame(rows)
