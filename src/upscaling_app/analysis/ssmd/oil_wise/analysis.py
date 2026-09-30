from __future__ import annotations

import numpy as np
import pandas as pd

from upscaling_app.upscaling.ssmd.physics.model import (
    momentum_response,
)


def _require_columns(
    data: pd.DataFrame,
    columns: list[str],
    *,
    source: str,
) -> None:
    missing = [column for column in columns if column not in data.columns]

    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def build_global_oil_factors(
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        predictions,
        [
            "oil_id",
            "eta",
            "momentum_amplification",
            "dR_pred",
        ],
        source="Global SSMD predictions",
    )

    data = predictions.copy()

    momentum = momentum_response(
        eta=data["eta"].to_numpy(dtype=float),
        momentum_amplification=data["momentum_amplification"].to_numpy(dtype=float),
    )

    data["k_global"] = data["dR_pred"].to_numpy(dtype=float) / momentum

    invalid = ~np.isfinite(data["k_global"]) | (data["k_global"] <= 0.0)

    if invalid.any():
        raise ValueError("Global SSMD factors must be finite and positive.")

    return (
        data.groupby(
            "oil_id",
            as_index=False,
        )
        .agg(
            k_global=("k_global", "mean"),
            k_global_std=("k_global", "std"),
            k_global_min=("k_global", "min"),
            k_global_max=("k_global", "max"),
            n_experiments_global=("k_global", "size"),
        )
        .sort_values("oil_id")
        .reset_index(drop=True)
    )


def build_oil_wise_comparison(
    global_predictions: pd.DataFrame,
    oil_wise_calibrations: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        oil_wise_calibrations,
        [
            "oil_id",
            "k_coef",
            "k_std",
            "n_experiments",
        ],
        source="Oil-wise SSMD calibrations",
    )

    global_factors = build_global_oil_factors(
        global_predictions,
    )

    oil_wise = oil_wise_calibrations[
        [
            "oil_id",
            "k_coef",
            "k_std",
            "n_experiments",
        ]
    ].rename(
        columns={
            "k_coef": "k_oil",
            "k_std": "k_oil_std",
            "n_experiments": "n_experiments_oil_wise",
        }
    )

    duplicated = oil_wise["oil_id"].duplicated(
        keep=False,
    )

    if duplicated.any():
        duplicate_rows = oil_wise.loc[
            duplicated,
            [
                "oil_id",
                "k_oil",
            ],
        ]

        raise ValueError(
            "Multiple oil-wise factors found for the same oil:\n"
            f"{duplicate_rows.to_string(index=False)}"
        )

    comparison = global_factors.merge(
        oil_wise,
        on="oil_id",
        how="inner",
        validate="one_to_one",
    )

    if len(comparison) != len(global_factors):
        raise ValueError(
            "Oil-wise calibrations do not cover all oils "
            "present in the global predictions."
        )

    comparison["delta_k"] = comparison["k_oil"] - comparison["k_global"]

    comparison["k_ratio"] = comparison["k_oil"] / comparison["k_global"]

    comparison["log_k_ratio"] = np.log(comparison["k_ratio"])

    comparison["relative_difference_pct"] = 100.0 * (comparison["k_ratio"] - 1.0)

    comparison["k_oil_cv_pct"] = 100.0 * comparison["k_oil_std"] / comparison["k_oil"]

    comparison["k_global_cv_pct"] = (
        100.0 * comparison["k_global_std"] / comparison["k_global"]
    )

    numeric_columns = [
        "k_global",
        "k_oil",
        "delta_k",
        "k_ratio",
        "log_k_ratio",
        "relative_difference_pct",
        "k_oil_cv_pct",
        "k_global_cv_pct",
    ]

    if (~np.isfinite(comparison[numeric_columns].to_numpy(dtype=float))).any():
        raise ValueError("Oil-wise comparison contains non-finite values.")

    return comparison.sort_values("oil_id").reset_index(
        drop=True,
    )


def summarize_oil_wise_comparison(
    comparison: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        comparison,
        [
            "oil_id",
            "k_global",
            "k_oil",
            "log_k_ratio",
            "relative_difference_pct",
        ],
        source="Oil-wise SSMD comparison",
    )

    log_ratio = comparison["log_k_ratio"].to_numpy(dtype=float)

    relative_difference = comparison["relative_difference_pct"].to_numpy(dtype=float)

    return pd.DataFrame(
        [
            {
                "n_oils": len(comparison),
                "mean_k_global": float(comparison["k_global"].mean()),
                "mean_k_oil": float(comparison["k_oil"].mean()),
                "mean_abs_relative_difference_pct": float(
                    np.mean(np.abs(relative_difference))
                ),
                "mean_log_k_ratio": float(np.mean(log_ratio)),
                "rmse_log_k_ratio": float(np.sqrt(np.mean(log_ratio**2))),
            }
        ]
    )
