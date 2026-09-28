from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.ssmd.metrics import (
    add_point_metrics,
    calculate_global_metrics,
)
from upscaling_app.upscaling.ssmd.versions import (
    REGRESSED_CD_GLOBAL,
    REGRESSED_OIL_WISE,
    SINTEF_BASELINE,
)

MODEL_VERSIONS = {
    "reference": SINTEF_BASELINE,
    "global": REGRESSED_CD_GLOBAL,
    "oil_wise": REGRESSED_OIL_WISE,
}

REGIME_ORDER = [
    "3 mm — no gas",
    "2 mm — no gas",
    "2 mm — gas",
]


@dataclass(frozen=True)
class SSMDPerformanceComparison:
    predictions: pd.DataFrame
    overall: pd.DataFrame
    by_regime: pd.DataFrame


def _load_metadata() -> pd.DataFrame:
    return pd.read_excel(
        paths.EXPERIMENTS_DATABASE,
        usecols=[
            "experiment_id",
            "oil_id",
            "nozzle_diameter",
            "has_gas",
            "water_jet_fraction",
        ],
    )


def _add_regime(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    is_3mm = (
        result["nozzle_diameter"].eq(0.003)
        & ~result["has_gas"]
    )
    is_2mm = (
        result["nozzle_diameter"].eq(0.002)
        & ~result["has_gas"]
    )
    is_2mm_gas = (
        result["nozzle_diameter"].eq(0.002)
        & result["has_gas"]
    )

    result["regime"] = np.select(
        [is_3mm, is_2mm, is_2mm_gas],
        REGIME_ORDER,
        default=None,
    )

    if result["regime"].isna().any():
        raise ValueError("Unsupported SSMD regime found in performance analysis.")

    return result


def _prepare_model(
    model: str,
    version: str,
    metadata: pd.DataFrame,
) -> pd.DataFrame:
    predictions = pd.read_excel(paths.SSMD_RESULTS)

    results = predictions.loc[
        predictions["model_version"].eq(version)
    ].copy()

    if results.empty:
        raise ValueError(
            f"No SSMD predictions found for {version!r}."
        )

    missing = [
        column
        for column in metadata.columns
        if column != "experiment_id"
        and column not in results.columns
    ]

    if missing:
        results = results.merge(
            metadata[["experiment_id", *missing]],
            on="experiment_id",
            how="left",
            validate="many_to_one",
        )

    results = _add_regime(results)
    results = add_point_metrics(results)
    results["model"] = model

    return results


def build_ssmd_performance_comparison() -> SSMDPerformanceComparison:
    metadata = _load_metadata()

    frames = [
        _prepare_model(
            model,
            version,
            metadata,
        )
        for model, version in MODEL_VERSIONS.items()
    ]

    predictions = pd.concat(
        frames,
        ignore_index=True,
    )

    overall_rows = []

    for model, group in predictions.groupby(
        "model",
        sort=False,
    ):
        metrics = calculate_global_metrics(group)
        overall_rows.append(
            {
                "model": model,
                "n": len(group),
                **metrics,
            }
        )

    regime_rows = []

    for (model, regime), group in predictions.groupby(
        ["model", "regime"],
        sort=False,
    ):
        metrics = calculate_global_metrics(group)
        regime_rows.append(
            {
                "model": model,
                "regime": regime,
                "n": len(group),
                **metrics,
            }
        )

    by_regime = pd.DataFrame(regime_rows)
    by_regime["regime"] = pd.Categorical(
        by_regime["regime"],
        categories=REGIME_ORDER,
        ordered=True,
    )
    by_regime = by_regime.sort_values(
        ["model", "regime"],
    ).reset_index(drop=True)

    return SSMDPerformanceComparison(
        predictions=predictions,
        overall=pd.DataFrame(overall_rows),
        by_regime=by_regime,
    )
