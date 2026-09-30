from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from upscaling_app import paths

if TYPE_CHECKING:
    from upscaling_app.analysis.ssmd.oil_wise.pipeline import (
        SSMDOilWiseResult,
    )


COMPARISON_COLUMNS = [
    "oil_id",
    "k_global",
    "k_global_std",
    "k_global_min",
    "k_global_max",
    "n_experiments_global",
    "k_oil",
    "k_oil_std",
    "n_experiments_oil_wise",
    "delta_k",
    "k_ratio",
    "log_k_ratio",
    "relative_difference_pct",
    "k_global_cv_pct",
    "k_oil_cv_pct",
]

SUMMARY_COLUMNS = [
    "n_oils",
    "mean_k_global",
    "mean_k_oil",
    "mean_abs_relative_difference_pct",
    "mean_log_k_ratio",
    "rmse_log_k_ratio",
]


def _require_columns(
    data: pd.DataFrame,
    columns: list[str],
    *,
    source: str,
) -> None:
    missing = [column for column in columns if column not in data.columns]

    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def _validate_comparison(
    comparison: pd.DataFrame,
) -> None:
    if comparison.empty:
        raise ValueError("SSMD oil-wise comparison cannot be empty.")

    _require_columns(
        comparison,
        COMPARISON_COLUMNS,
        source="SSMD oil-wise comparison",
    )

    duplicated = comparison["oil_id"].duplicated(
        keep=False,
    )

    if duplicated.any():
        duplicate_rows = comparison.loc[
            duplicated,
            ["oil_id"],
        ]

        raise ValueError(
            "Duplicate oils found in SSMD oil-wise comparison:\n"
            f"{duplicate_rows.to_string(index=False)}"
        )


def _validate_summary(
    summary: pd.DataFrame,
) -> None:
    if len(summary) != 1:
        raise ValueError("SSMD oil-wise summary must contain exactly one row.")

    _require_columns(
        summary,
        SUMMARY_COLUMNS,
        source="SSMD oil-wise summary",
    )


def save_oil_wise_results(
    result: SSMDOilWiseResult,
) -> None:
    _validate_comparison(
        result.comparison,
    )

    _validate_summary(
        result.summary,
    )

    output = paths.SSMD_OIL_WISE_RESULTS_PATH

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    comparison = result.comparison.copy()
    summary = result.summary.copy()

    comparison.insert(
        0,
        "ssdi_source_version",
        result.ssdi_source_version,
    )

    summary.insert(
        0,
        "ssdi_source_version",
        result.ssdi_source_version,
    )

    comparison = comparison.sort_values("oil_id").reset_index(
        drop=True,
    )

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:
        comparison.to_excel(
            writer,
            sheet_name="comparison",
            index=False,
        )

        summary.to_excel(
            writer,
            sheet_name="summary",
            index=False,
        )
