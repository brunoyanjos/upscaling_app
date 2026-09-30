from __future__ import annotations

from pathlib import Path

import pandas as pd

from upscaling_app import paths

PREDICTION_VERSION_KEYS = [
    "ssmd_model_version",
    "ssdi_source_version",
]

PREDICTION_ID_KEYS = [
    "experiment_id",
    *PREDICTION_VERSION_KEYS,
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


def _validate_predictions(
    predictions: pd.DataFrame,
) -> None:
    _require_columns(
        predictions,
        PREDICTION_ID_KEYS,
        source="SSMD predictions",
    )

    if predictions.empty:
        raise ValueError("SSMD prediction table is empty.")

    missing_version = predictions[PREDICTION_VERSION_KEYS].isna().any(axis=1)

    if missing_version.any():
        raise ValueError("SSMD prediction table contains missing model versions.")

    duplicated = predictions.duplicated(
        subset=PREDICTION_ID_KEYS,
        keep=False,
    )

    if duplicated.any():
        duplicate_rows = predictions.loc[
            duplicated,
            PREDICTION_ID_KEYS,
        ]

        raise ValueError(
            "Duplicate SSMD predictions found:\n"
            f"{duplicate_rows.to_string(index=False)}"
        )


def _validate_calibrations(
    calibrations: pd.DataFrame,
) -> None:
    _require_columns(
        calibrations,
        [
            "ssmd_model_version",
        ],
        source="SSMD calibrations",
    )

    if calibrations.empty:
        raise ValueError("SSMD calibration table is empty.")

    if calibrations["ssmd_model_version"].isna().any():
        raise ValueError("SSMD calibration table contains missing model versions.")

    if "oil_id" not in calibrations.columns:
        duplicated = calibrations.duplicated(
            subset=[
                "ssmd_model_version",
            ],
            keep=False,
        )

        if duplicated.any():
            raise ValueError(
                "Multiple global calibrations found for the same " "SSMD model version."
            )

        return

    oil_wise = calibrations["oil_id"].notna()
    global_rows = ~oil_wise

    duplicated_oil = calibrations.loc[oil_wise].duplicated(
        subset=[
            "ssmd_model_version",
            "oil_id",
        ],
        keep=False,
    )

    if duplicated_oil.any():
        duplicate_rows = calibrations.loc[oil_wise].loc[
            duplicated_oil,
            [
                "ssmd_model_version",
                "oil_id",
            ],
        ]

        raise ValueError(
            "Duplicate oil-wise SSMD calibrations found:\n"
            f"{duplicate_rows.to_string(index=False)}"
        )

    duplicated_global = calibrations.loc[global_rows].duplicated(
        subset=[
            "ssmd_model_version",
        ],
        keep=False,
    )

    if duplicated_global.any():
        raise ValueError(
            "Multiple global calibrations found for the same " "SSMD model version."
        )


def save_predictions(
    predictions: pd.DataFrame,
    path: Path = paths.SSMD_PREDICTIONS_PATH,
) -> None:
    _validate_predictions(
        predictions,
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    versions = predictions[PREDICTION_VERSION_KEYS].drop_duplicates()

    if path.exists():
        existing = pd.read_excel(
            path,
        )

        _require_columns(
            existing,
            PREDICTION_ID_KEYS,
            source="Existing SSMD predictions",
        )

        existing = existing.merge(
            versions.assign(
                _replace=True,
            ),
            on=PREDICTION_VERSION_KEYS,
            how="left",
        )

        existing = existing.loc[existing["_replace"].isna()].drop(
            columns=[
                "_replace",
            ]
        )

        output = pd.concat(
            [
                existing,
                predictions,
            ],
            ignore_index=True,
        )

    else:
        output = predictions.copy()

    _validate_predictions(
        output,
    )

    sort_columns = [
        "ssmd_model_version",
        "ssdi_source_version",
    ]

    if "oil_id" in output.columns:
        sort_columns.append("oil_id")

    sort_columns.append("experiment_id")

    output = output.sort_values(
        sort_columns,
    ).reset_index(
        drop=True,
    )

    output.to_excel(
        path,
        index=False,
    )


def save_calibrations(
    calibrations: pd.DataFrame,
    path: Path = paths.SSMD_CALIBRATIONS_PATH,
) -> None:
    _validate_calibrations(
        calibrations,
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_versions = calibrations["ssmd_model_version"].drop_duplicates()

    if path.exists():
        existing = pd.read_excel(
            path,
        )

        _require_columns(
            existing,
            [
                "ssmd_model_version",
            ],
            source="Existing SSMD calibrations",
        )

        existing = existing.loc[
            ~existing["ssmd_model_version"].isin(model_versions)
        ].copy()

        output = pd.concat(
            [
                existing,
                calibrations,
            ],
            ignore_index=True,
        )

    else:
        output = calibrations.copy()

    _validate_calibrations(
        output,
    )

    sort_columns = [
        "ssmd_model_version",
    ]

    if "oil_id" in output.columns:
        sort_columns.append("oil_id")

    output = output.sort_values(
        sort_columns,
        na_position="first",
    ).reset_index(
        drop=True,
    )

    output.to_excel(
        path,
        index=False,
    )
