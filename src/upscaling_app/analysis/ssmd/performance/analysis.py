from __future__ import annotations

import pandas as pd

from upscaling_app.analysis.ssmd.metrics import (
    calculate_metrics,
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


def evaluate_relative_performance(
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        predictions,
        [
            "ssmd_model_version",
            "ssdi_source_version",
            "dR_exp",
            "dR_pred",
        ],
        source="SSMD predictions",
    )

    model_versions = predictions["ssmd_model_version"].dropna().unique()

    if len(model_versions) != 1:
        raise ValueError(
            "Relative performance requires exactly " "one SSMD model version."
        )

    ssdi_versions = predictions["ssdi_source_version"].dropna().unique()

    if len(ssdi_versions) != 1:
        raise ValueError(
            "Relative performance requires exactly " "one SSDI source version."
        )

    metrics = calculate_metrics(
        predictions["dR_exp"].to_numpy(
            dtype=float,
        ),
        predictions["dR_pred"].to_numpy(
            dtype=float,
        ),
    )

    return pd.DataFrame(
        [
            {
                "ssmd_model_version": model_versions[0],
                "ssdi_source_version": ssdi_versions[0],
                **metrics,
            }
        ]
    )


def evaluate_end_to_end_performance(
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        predictions,
        [
            "ssmd_model_version",
            "ssdi_source_version",
            "d50_exp",
            "d50_pred",
        ],
        source="SSMD predictions",
    )

    model_versions = predictions["ssmd_model_version"].dropna().unique()

    if len(model_versions) != 1:
        raise ValueError(
            "End-to-end performance requires exactly " "one SSMD model version."
        )

    ssdi_versions = predictions["ssdi_source_version"].dropna().unique()

    if len(ssdi_versions) != 1:
        raise ValueError(
            "End-to-end performance requires exactly " "one SSDI source version."
        )

    metrics = calculate_metrics(
        predictions["d50_exp"].to_numpy(
            dtype=float,
        ),
        predictions["d50_pred"].to_numpy(
            dtype=float,
        ),
    )

    return pd.DataFrame(
        [
            {
                "ssmd_model_version": model_versions[0],
                "ssdi_source_version": ssdi_versions[0],
                **metrics,
            }
        ]
    )


def build_performance_comparison(
    reference: pd.DataFrame,
    global_model: pd.DataFrame,
) -> pd.DataFrame:
    reference_version = reference["ssdi_source_version"].dropna().unique()

    global_version = global_model["ssdi_source_version"].dropna().unique()

    if (
        len(reference_version) != 1
        or len(global_version) != 1
        or reference_version[0] != global_version[0]
    ):
        raise ValueError(
            "SSMD model comparison requires " "the same SSDI source version."
        )

    reference_ids = set(reference["experiment_id"])

    global_ids = set(global_model["experiment_id"])

    if reference_ids != global_ids:
        raise ValueError(
            "SSMD model comparison requires " "identical experiment populations."
        )

    relative_reference = evaluate_relative_performance(
        reference,
    )

    relative_global = evaluate_relative_performance(
        global_model,
    )

    end_to_end_reference = evaluate_end_to_end_performance(
        reference,
    )

    end_to_end_global = evaluate_end_to_end_performance(
        global_model,
    )

    relative = pd.concat(
        [
            relative_reference,
            relative_global,
        ],
        ignore_index=True,
    )

    relative.insert(
        2,
        "evaluation_target",
        "dR",
    )

    end_to_end = pd.concat(
        [
            end_to_end_reference,
            end_to_end_global,
        ],
        ignore_index=True,
    )

    end_to_end.insert(
        2,
        "evaluation_target",
        "d50",
    )

    return pd.concat(
        [
            relative,
            end_to_end,
        ],
        ignore_index=True,
    )
