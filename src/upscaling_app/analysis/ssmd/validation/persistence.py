from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from upscaling_app import paths

if TYPE_CHECKING:
    from upscaling_app.analysis.ssmd.validation.pipeline import (
        SSMDValidationResult,
    )


PREDICTION_COLUMNS = [
    "experiment_id",
    "oil_id",
    "held_out_oil_id",
    "nozzle_diameter",
    "has_gas",
    "water_jet_fraction",
    "n_train",
    "n_test",
    "n_train_oils",
    "c_coef",
    "d_coef",
    "eta",
    "momentum_amplification",
    "dR_exp",
    "dR_pred",
    "log_residual",
]

BY_OIL_COLUMNS = [
    "oil_id",
    "n_train",
    "n_test",
    "n_train_oils",
    "c_coef",
    "d_coef",
    "n",
    "log_mse",
    "r2_log",
    "rmse",
    "mape_pct",
    "mean_log_residual",
    "std_log_residual",
]

SUMMARY_COLUMNS = [
    "n_oils",
    "n",
    "log_mse",
    "r2_log",
    "rmse",
    "mape_pct",
    "mean_log_residual",
    "std_log_residual",
]

COMPARISON_COLUMNS = [
    "evaluation",
    "n",
    "log_mse",
    "r2_log",
    "rmse",
    "mape_pct",
    "mean_log_residual",
    "std_log_residual",
    "log_mse_change_pct",
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


def _validate_result(
    result: SSMDValidationResult,
) -> None:
    if result.predictions.empty:
        raise ValueError("SSMD validation predictions cannot be empty.")

    if result.by_oil.empty:
        raise ValueError("SSMD validation oil summary cannot be empty.")

    if len(result.summary) != 1:
        raise ValueError("SSMD validation summary must contain exactly one row.")

    if len(result.comparison) != 2:
        raise ValueError("SSMD validation comparison must contain exactly two rows.")

    _require_columns(
        result.predictions,
        PREDICTION_COLUMNS,
        source="SSMD validation predictions",
    )

    _require_columns(
        result.by_oil,
        BY_OIL_COLUMNS,
        source="SSMD validation oil summary",
    )

    _require_columns(
        result.summary,
        SUMMARY_COLUMNS,
        source="SSMD validation summary",
    )

    _require_columns(
        result.comparison,
        COMPARISON_COLUMNS,
        source="SSMD validation comparison",
    )

    duplicated = result.predictions["experiment_id"].duplicated(
        keep=False,
    )

    if duplicated.any():
        duplicate_rows = result.predictions.loc[
            duplicated,
            [
                "experiment_id",
                "oil_id",
            ],
        ]

        raise ValueError(
            "Duplicate experiments found in SSMD validation results:\n"
            f"{duplicate_rows.to_string(index=False)}"
        )

    duplicated_oils = result.by_oil["oil_id"].duplicated(
        keep=False,
    )

    if duplicated_oils.any():
        duplicate_rows = result.by_oil.loc[
            duplicated_oils,
            [
                "oil_id",
            ],
        ]

        raise ValueError(
            "Duplicate oil folds found in SSMD validation results:\n"
            f"{duplicate_rows.to_string(index=False)}"
        )


def save_validation_results(
    result: SSMDValidationResult,
) -> None:
    _validate_result(
        result,
    )

    output = paths.SSMD_VALIDATION_RESULTS_PATH

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    predictions = result.predictions.copy()
    by_oil = result.by_oil.copy()
    summary = result.summary.copy()
    comparison = result.comparison.copy()

    predictions.insert(
        0,
        "ssdi_source_version",
        result.ssdi_source_version,
    )

    by_oil.insert(
        0,
        "ssdi_source_version",
        result.ssdi_source_version,
    )

    summary.insert(
        0,
        "ssdi_source_version",
        result.ssdi_source_version,
    )

    comparison.insert(
        0,
        "ssdi_source_version",
        result.ssdi_source_version,
    )

    predictions = predictions.sort_values(
        [
            "oil_id",
            "experiment_id",
        ]
    ).reset_index(
        drop=True,
    )

    by_oil = by_oil.sort_values("oil_id").reset_index(
        drop=True,
    )

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:
        predictions.to_excel(
            writer,
            sheet_name="predictions",
            index=False,
        )

        by_oil.to_excel(
            writer,
            sheet_name="by_oil",
            index=False,
        )

        summary.to_excel(
            writer,
            sheet_name="summary",
            index=False,
        )

        comparison.to_excel(
            writer,
            sheet_name="comparison",
            index=False,
        )
