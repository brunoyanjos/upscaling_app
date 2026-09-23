import numpy as np
import pandas as pd

from upscaling_app.analysis.ssdi.io.data import load_ssdi_results
from upscaling_app.analysis.ssdi.metrics import (
    add_point_metrics,
    calculate_global_metrics,
)
from upscaling_app.analysis.ssdi.outliers import mark_iqr_outliers
from upscaling_app.upscaling.ssdi.versions import (
    BASELINE_VERSION,
    REFERENCE_VERSION,
    FILTERED_VERSION,
    OIL_SENSITIVITY_VERSION,
)

MODEL_VERSIONS = [
    BASELINE_VERSION,
    REFERENCE_VERSION,
    FILTERED_VERSION,
    OIL_SENSITIVITY_VERSION,
]


def build_model_comparison() -> pd.DataFrame:
    rows = []

    for version in MODEL_VERSIONS:
        results = load_ssdi_results(version)

        results = add_point_metrics(results)

        results = mark_iqr_outliers(results)

        metrics = calculate_global_metrics(results)

        log_mse = float(np.mean(results["log_residual"] ** 2))

        rows.append(
            {
                "model_version": version,
                "n": len(results),
                "a": results["a_coef"].iloc[0],
                "b": results["b_coef"].iloc[0],
                "log_mse": log_mse,
                "r2": metrics["r2"],
                "rmse": metrics["rmse"],
                "mape": metrics["mape"],
                "outlier_count": int(results["is_outlier"].sum()),
            }
        )

    return pd.DataFrame(rows)


def build_evaluation_comparison(
    loo_result,
) -> pd.DataFrame:
    rows = []

    for version in MODEL_VERSIONS:
        results = load_ssdi_results(version)

        results = add_point_metrics(results)

        metrics = calculate_global_metrics(results)

        log_mse = float(np.mean(results["log_residual"] ** 2))

        rows.append(
            {
                "model_version": version,
                "evaluation": "in_sample",
                "n": len(results),
                "log_mse": log_mse,
                "r2": metrics["r2"],
                "rmse": metrics["rmse"],
                "mape": metrics["mape"],
            }
        )

    metrics = loo_result.global_metrics

    rows.append(
        {
            "model_version": "leave_one_oil_out",
            "evaluation": "out_of_oil",
            "n": metrics["n"],
            "log_mse": metrics["log_mse"],
            "r2": metrics["r2"],
            "rmse": metrics["rmse"],
            "mape": metrics["mape"],
        }
    )

    return pd.DataFrame(rows)
