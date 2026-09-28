from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.ssmd.metrics import (
    add_point_metrics,
    calculate_global_metrics,
)
from upscaling_app.upscaling.ssmd.versions import (
    REGRESSED_CD_GLOBAL,
    REGRESSED_OIL_WISE,
)


@dataclass(frozen=True)
class SSMDLocalComparison:
    by_oil: pd.DataFrame
    overall: pd.DataFrame


def _load_metadata() -> pd.DataFrame:
    return pd.read_excel(
        paths.EXPERIMENTS_DATABASE,
        usecols=[
            "experiment_id",
            "oil_id",
        ],
    )


def _prepare_results(
    model_version: str,
) -> pd.DataFrame:
    results = pd.read_excel(paths.SSMD_RESULTS)

    results = results.loc[
        results["model_version"].eq(model_version)
    ].copy()

    if results.empty:
        raise ValueError(
            f"No SSMD predictions found for {model_version!r}."
        )

    metadata = _load_metadata()

    if "oil_id" not in results.columns:
        results = results.merge(
            metadata,
            on="experiment_id",
            how="left",
            validate="many_to_one",
        )

    return add_point_metrics(results)


def _metrics_by_oil(
    results: pd.DataFrame,
    suffix: str,
) -> pd.DataFrame:
    rows = []

    for oil_id, group in results.groupby(
        "oil_id",
        sort=True,
    ):
        metrics = calculate_global_metrics(group)

        rows.append(
            {
                "oil_id": oil_id,
                "n": len(group),
                f"log_mse_{suffix}": metrics["log_mse"],
                f"r2_{suffix}": metrics["r2"],
                f"rmse_{suffix}": metrics["rmse"],
                f"mape_{suffix}": metrics["mape"],
            }
        )

    return pd.DataFrame(rows)


def build_oil_wise_comparison() -> SSMDLocalComparison:
    global_results = _prepare_results(
        REGRESSED_CD_GLOBAL,
    )

    local_results = _prepare_results(
        REGRESSED_OIL_WISE,
    )

    global_by_oil = _metrics_by_oil(
        global_results,
        "global",
    )

    local_by_oil = _metrics_by_oil(
        local_results,
        "local",
    )

    calibrations = pd.read_excel(
        paths.SSMD_CALIBRATIONS,
    )

    calibrations = calibrations.loc[
        calibrations["model_version"].eq(
            REGRESSED_OIL_WISE
        ),
        [
            "oil_id",
            "k_coef",
        ],
    ].copy()

    by_oil = (
        global_by_oil
        .merge(
            local_by_oil,
            on=["oil_id", "n"],
            validate="one_to_one",
        )
        .merge(
            calibrations,
            on="oil_id",
            validate="one_to_one",
        )
    )

    by_oil["log_mse_reduction_pct"] = 100.0 * (
        1.0
        - by_oil["log_mse_local"]
        / by_oil["log_mse_global"]
    )

    by_oil = by_oil[
        [
            "oil_id",
            "n",
            "k_coef",
            "log_mse_global",
            "log_mse_local",
            "log_mse_reduction_pct",
            "r2_global",
            "r2_local",
            "rmse_global",
            "rmse_local",
            "mape_global",
            "mape_local",
        ]
    ].sort_values("oil_id").reset_index(drop=True)

    overall_rows = []

    for label, results in [
        ("global", global_results),
        ("oil_wise", local_results),
    ]:
        metrics = calculate_global_metrics(results)

        overall_rows.append(
            {
                "model": label,
                "n": len(results),
                **metrics,
            }
        )

    return SSMDLocalComparison(
        by_oil=by_oil,
        overall=pd.DataFrame(overall_rows),
    )
