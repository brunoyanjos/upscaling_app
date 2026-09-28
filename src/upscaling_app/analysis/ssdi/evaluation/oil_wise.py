from dataclasses import dataclass

import pandas as pd

from upscaling_app.analysis.ssdi.evaluation.oil_analysis import (
    add_oil_metadata,
    calculate_oil_metrics,
)
from upscaling_app.analysis.ssdi.io.data import (
    load_ssdi_calibrations,
    load_ssdi_results,
)
from upscaling_app.analysis.ssdi.metrics import (
    add_point_metrics,
    calculate_global_metrics,
)
from upscaling_app.analysis.ssdi.outliers import (
    mark_iqr_outliers,
)
from upscaling_app.upscaling.ssdi.versions import (
    BASELINE_VERSION,
    OIL_WISE_VERSION,
)


@dataclass(frozen=True)
class OilWiseComparisonResult:
    by_oil: pd.DataFrame
    overall: pd.DataFrame


def _prepare_results(
    model_version: str,
) -> pd.DataFrame:
    results = load_ssdi_results(
        model_version,
    )

    results = add_oil_metadata(
        results,
    )

    results = add_point_metrics(
        results,
    )

    results = mark_iqr_outliers(
        results,
    )

    return results


def build_oil_wise_comparison() -> OilWiseComparisonResult:
    global_results = _prepare_results(
        BASELINE_VERSION,
    )

    local_results = _prepare_results(
        OIL_WISE_VERSION,
    )

    calibrations = load_ssdi_calibrations(
        OIL_WISE_VERSION,
    )

    global_by_oil = calculate_oil_metrics(
        global_results,
    )

    local_by_oil = calculate_oil_metrics(
        local_results,
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
            "log_mse": "log_mse_local",
        }
    )

    coefficients = calibrations[
        [
            "oil_id",
            "a_optimized",
            "b_optimized",
        ]
    ].rename(
        columns={
            "a_optimized": "a_local",
            "b_optimized": "b_local",
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
        1.0 - by_oil["log_mse_local"] / by_oil["log_mse_global"]
    )

    by_oil = (
        by_oil[
            [
                "oil_id",
                "n",
                "a_local",
                "b_local",
                "log_mse_global",
                "log_mse_local",
                "log_mse_reduction_pct",
            ]
        ]
        .sort_values("oil_id")
        .reset_index(drop=True)
    )

    overall_rows = []

    for label, results in [
        (
            "global",
            global_results,
        ),
        (
            "oil_wise",
            local_results,
        ),
    ]:
        metrics = calculate_global_metrics(
            results,
        )

        overall_rows.append(
            {
                "model": label,
                "n": len(results),
                "log_mse": metrics["log_mse"],
                "r2": metrics["r2"],
                "rmse": metrics["rmse"],
                "mape": metrics["mape"],
            }
        )

    overall = pd.DataFrame(overall_rows)

    return OilWiseComparisonResult(
        by_oil=by_oil,
        overall=overall,
    )
