from __future__ import annotations

import pandas as pd

from upscaling_app import paths

PREDICTION_KEYS = [
    "experiment_id",
    "ssmd_model_version",
    "ssdi_source_version",
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


def load_predictions() -> pd.DataFrame:
    if not paths.SSMD_PREDICTIONS_PATH.exists():
        raise FileNotFoundError(
            "SSMD predictions were not found. " "Run an SSMD modelling workflow first."
        )

    predictions = pd.read_excel(
        paths.SSMD_PREDICTIONS_PATH,
    )

    _require_columns(
        predictions,
        [
            "experiment_id",
            "oil_id",
            "nozzle_diameter",
            "has_gas",
            "water_jet_fraction",
            "ssmd_model_version",
            "ssdi_source_version",
            "eta",
            "momentum_amplification",
            "dR_exp",
            "dR_pred",
            "d50_exp",
            "untreated_d50_exp",
            "untreated_d50_pred",
            "d50_pred",
        ],
        source="SSMD predictions",
    )

    duplicated = predictions.duplicated(
        subset=PREDICTION_KEYS,
        keep=False,
    )

    if duplicated.any():
        duplicate_rows = predictions.loc[
            duplicated,
            PREDICTION_KEYS,
        ]

        raise ValueError(
            "Duplicate persisted SSMD predictions found:\n"
            f"{duplicate_rows.to_string(index=False)}"
        )

    return predictions


def load_calibrations() -> pd.DataFrame:
    if not paths.SSMD_CALIBRATIONS_PATH.exists():
        raise FileNotFoundError(
            "SSMD calibrations were not found. "
            "Run an SSMD calibration workflow first."
        )

    calibrations = pd.read_excel(
        paths.SSMD_CALIBRATIONS_PATH,
    )

    _require_columns(
        calibrations,
        [
            "ssmd_model_version",
        ],
        source="SSMD calibrations",
    )

    return calibrations


def select_predictions(
    predictions: pd.DataFrame,
    *,
    ssmd_model_version: str,
    ssdi_source_version: str,
) -> pd.DataFrame:
    _require_columns(
        predictions,
        [
            "ssmd_model_version",
            "ssdi_source_version",
        ],
        source="SSMD predictions",
    )

    selected = predictions.loc[
        predictions["ssmd_model_version"].eq(ssmd_model_version)
        & predictions["ssdi_source_version"].eq(ssdi_source_version)
    ].copy()

    if selected.empty:
        raise ValueError(
            "No SSMD predictions found for "
            f"ssmd_model_version={ssmd_model_version!r} and "
            f"ssdi_source_version={ssdi_source_version!r}."
        )

    duplicated = selected["experiment_id"].duplicated(
        keep=False,
    )

    if duplicated.any():
        duplicate_rows = selected.loc[
            duplicated,
            [
                "experiment_id",
                "ssmd_model_version",
                "ssdi_source_version",
            ],
        ]

        raise ValueError(
            "Multiple SSMD predictions found for the same experiment:\n"
            f"{duplicate_rows.to_string(index=False)}"
        )

    return selected.reset_index(
        drop=True,
    )


def load_model_predictions(
    *,
    ssmd_model_version: str,
    ssdi_source_version: str,
) -> pd.DataFrame:
    predictions = load_predictions()

    return select_predictions(
        predictions,
        ssmd_model_version=ssmd_model_version,
        ssdi_source_version=ssdi_source_version,
    )


def select_calibrations(
    calibrations: pd.DataFrame,
    *,
    ssmd_model_version: str,
) -> pd.DataFrame:
    _require_columns(
        calibrations,
        [
            "ssmd_model_version",
        ],
        source="SSMD calibrations",
    )

    selected = calibrations.loc[
        calibrations["ssmd_model_version"].eq(ssmd_model_version)
    ].copy()

    if selected.empty:
        raise ValueError(
            "No SSMD calibration found for "
            f"ssmd_model_version={ssmd_model_version!r}."
        )

    return selected.reset_index(
        drop=True,
    )


def load_model_calibrations(
    *,
    ssmd_model_version: str,
) -> pd.DataFrame:
    calibrations = load_calibrations()

    return select_calibrations(
        calibrations,
        ssmd_model_version=ssmd_model_version,
    )
