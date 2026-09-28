from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.ssdi.io.data import (
    load_ssdi_results,
)
from upscaling_app.analysis.ssdi.metrics import (
    add_point_metrics,
    calculate_global_metrics,
)
from upscaling_app.upscaling.ssdi.versions import (
    BASELINE_VERSION,
    OIL_WISE_VERSION,
    REFERENCE_VERSION,
)

MODEL_VERSIONS = {
    "reference": REFERENCE_VERSION,
    "global": BASELINE_VERSION,
    "oil_wise": OIL_WISE_VERSION,
}


@dataclass(frozen=True)
class SSDIPerformanceComparison:
    predictions: pd.DataFrame
    overall: pd.DataFrame
    by_gas: pd.DataFrame


def _load_experiment_metadata() -> pd.DataFrame:
    return pd.read_excel(
        paths.EXPERIMENTS_DATABASE,
        usecols=[
            "experiment_id",
            "nozzle_diameter",
            "has_gas",
            "dispersion_tag",
        ],
    )


def _prepare_model_results(
    model: str,
    model_version: str,
    metadata: pd.DataFrame,
) -> pd.DataFrame:
    results = load_ssdi_results(
        model_version,
    )

    results = results.merge(
        metadata,
        on="experiment_id",
        how="left",
        validate="many_to_one",
    )

    results = add_point_metrics(
        results,
    )

    results["model"] = model

    return results


def build_ssdi_performance_comparison() -> SSDIPerformanceComparison:
    metadata = _load_experiment_metadata()

    prediction_frames = []

    for model, model_version in MODEL_VERSIONS.items():
        results = _prepare_model_results(
            model=model,
            model_version=model_version,
            metadata=metadata,
        )

        prediction_frames.append(
            results,
        )

    predictions = pd.concat(
        prediction_frames,
        ignore_index=True,
    )

    # ---------------------------------------------------------
    # Overall performance — complete 90-experiment population
    # ---------------------------------------------------------

    overall_rows = []

    for model, group in predictions.groupby(
        "model",
        sort=False,
    ):
        metrics = calculate_global_metrics(
            group,
        )

        overall_rows.append(
            {
                "model": model,
                "n": len(group),
                "log_mse": metrics["log_mse"],
                "r2": metrics["r2"],
                "rmse": metrics["rmse"],
                "mape": metrics["mape"],
                "mean_log_residual": float(group["log_residual"].mean()),
            }
        )

    overall = pd.DataFrame(overall_rows)

    # ---------------------------------------------------------
    # Gas comparison — restricted to 2 mm
    # ---------------------------------------------------------

    two_mm = predictions.loc[predictions["nozzle_diameter"] == 2e-3].copy()

    gas_rows = []

    for (
        model,
        has_gas,
    ), group in two_mm.groupby(
        [
            "model",
            "has_gas",
        ],
        sort=False,
    ):
        metrics = calculate_global_metrics(
            group,
        )

        gas_rows.append(
            {
                "model": model,
                "has_gas": bool(has_gas),
                "n": len(group),
                "log_mse": metrics["log_mse"],
                "r2": metrics["r2"],
                "rmse": metrics["rmse"],
                "mape": metrics["mape"],
                "mean_log_residual": float(group["log_residual"].mean()),
            }
        )

    by_gas = pd.DataFrame(gas_rows)

    return SSDIPerformanceComparison(
        predictions=predictions,
        overall=overall,
        by_gas=by_gas,
    )
