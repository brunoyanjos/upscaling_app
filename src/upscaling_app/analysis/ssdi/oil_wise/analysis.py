from dataclasses import dataclass

import pandas as pd

from upscaling_app.analysis.ssdi.io.data import (
    load_ssdi_calibrations,
    load_ssdi_results,
)
from upscaling_app.analysis.ssdi.metrics import (
    calculate_global_metrics,
)
from upscaling_app.analysis.ssdi.performance.analysis import (
    calculate_oil_metrics,
    prepare_performance_results,
)
from upscaling_app.upscaling.ssdi.versions import (
    BASELINE_VERSION,
    OIL_WISE_VERSION,
)


@dataclass(frozen=True)
class OilWiseComparisonResult:
    global_a: float
    global_b: float

    oil_wise_results: pd.DataFrame
    by_oil: pd.DataFrame
    overall: pd.DataFrame


def run_oil_wise_comparison_analysis() -> OilWiseComparisonResult:
    global_predictions = load_ssdi_results(
        BASELINE_VERSION,
    )

    oil_wise_predictions = load_ssdi_results(
        OIL_WISE_VERSION,
    )

    global_results = prepare_performance_results(
        global_predictions,
    )

    oil_wise_results = prepare_performance_results(
        oil_wise_predictions,
    )

    global_calibration = load_ssdi_calibrations(
        BASELINE_VERSION,
    )

    oil_wise_calibrations = load_ssdi_calibrations(
        OIL_WISE_VERSION,
    )

    if len(global_calibration) != 1:
        raise ValueError("Expected exactly one global SSDI baseline calibration.")

    global_a = float(global_calibration.iloc[0]["a_optimized"])

    global_b = float(global_calibration.iloc[0]["b_optimized"])

    global_by_oil = calculate_oil_metrics(
        global_results,
    )

    local_by_oil = calculate_oil_metrics(
        oil_wise_results,
    )

    global_by_oil = global_by_oil[
        [
            "oil_id",
            "n",
            "log_mse",
        ]
    ].rename(
        columns={
            "log_mse": "log_mse_global",
        }
    )

    local_by_oil = local_by_oil[
        [
            "oil_id",
            "n",
            "log_mse",
        ]
    ].rename(
        columns={
            "log_mse": "log_mse_oil_wise",
        }
    )

    coefficients = oil_wise_calibrations[
        [
            "oil_id",
            "a_optimized",
            "b_optimized",
        ]
    ].rename(
        columns={
            "a_optimized": "a_oil_wise",
            "b_optimized": "b_oil_wise",
        }
    )

    by_oil = global_by_oil.merge(
        local_by_oil,
        on=[
            "oil_id",
            "n",
        ],
        validate="one_to_one",
    ).merge(
        coefficients,
        on="oil_id",
        validate="one_to_one",
    )

    by_oil["log_mse_reduction_pct"] = 100.0 * (
        1.0 - by_oil["log_mse_oil_wise"] / by_oil["log_mse_global"]
    )

    by_oil = (
        by_oil[
            [
                "oil_id",
                "n",
                "a_oil_wise",
                "b_oil_wise",
                "log_mse_global",
                "log_mse_oil_wise",
                "log_mse_reduction_pct",
            ]
        ]
        .sort_values(
            "oil_id",
        )
        .reset_index(
            drop=True,
        )
    )

    overall_rows = []

    for model, results in (
        (
            "global",
            global_results,
        ),
        (
            "oil_wise",
            oil_wise_results,
        ),
    ):
        metrics = calculate_global_metrics(
            results,
        )

        overall_rows.append(
            {
                "model": model,
                "n": len(results),
                "log_mse": metrics["log_mse"],
                "r2": metrics["r2"],
                "rmse": metrics["rmse"],
                "mape": metrics["mape"],
                "mean_log_residual": float(results["log_residual"].mean()),
            }
        )

    overall = pd.DataFrame(
        overall_rows,
    )

    return OilWiseComparisonResult(
        global_a=global_a,
        global_b=global_b,
        oil_wise_results=oil_wise_results,
        by_oil=by_oil,
        overall=overall,
    )
