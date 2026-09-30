from __future__ import annotations

import numpy as np
import pandas as pd

from upscaling_app import paths

PAIR_KEYS = [
    "oil_id",
    "nozzle_diameter",
    "has_gas",
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


def load_experiments() -> pd.DataFrame:
    return pd.read_excel(
        paths.EXPERIMENTS_DATABASE,
    )


def load_ssmd_experiments() -> pd.DataFrame:
    experiments = load_experiments()

    _require_columns(
        experiments,
        [
            "dispersion_kind",
        ],
        source="Experiments database",
    )

    ssmd = experiments.loc[experiments["dispersion_kind"].eq("SSMD")].copy()

    if ssmd.empty:
        raise ValueError("No SSMD experiments were found in the normalized database.")

    return ssmd.reset_index(drop=True)


def _build_untreated_reference_table(
    experiments: pd.DataFrame,
) -> pd.DataFrame:
    required_columns = PAIR_KEYS + [
        "experiment_id",
        "dispersion_kind",
        "dispersion_tag",
        "measured_d50",
        "oil_flow",
        "gas_flow",
        "oil_density",
        "gas_density",
        "ift",
    ]

    _require_columns(
        experiments,
        required_columns,
        source="Experiments database",
    )

    untreated = experiments.loc[experiments["dispersion_kind"].eq("Untreated")].copy()

    if untreated.empty:
        raise ValueError(
            "No untreated experiments were found in the normalized database."
        )

    duplicated_reference = untreated.duplicated(
        subset=PAIR_KEYS,
        keep=False,
    )

    if duplicated_reference.any():
        duplicated = untreated.loc[
            duplicated_reference,
            PAIR_KEYS
            + [
                "experiment_id",
                "dispersion_tag",
            ],
        ]

        raise ValueError(
            "Multiple untreated references found for the same "
            "SSMD condition:\n"
            f"{duplicated.to_string(index=False)}"
        )

    untreated = untreated[
        PAIR_KEYS
        + [
            "experiment_id",
            "measured_d50",
            "oil_flow",
            "gas_flow",
            "oil_density",
            "gas_density",
            "ift",
        ]
    ].rename(
        columns={
            "experiment_id": "untreated_experiment_id",
            "measured_d50": "untreated_d50_measured",
            "oil_flow": "untreated_oil_flow",
            "gas_flow": "untreated_gas_flow",
            "oil_density": "untreated_oil_density",
            "gas_density": "untreated_gas_density",
            "ift": "untreated_ift",
        }
    )

    return untreated.reset_index(drop=True)


def load_ssmd_calibration_dataset() -> pd.DataFrame:
    experiments = load_experiments()

    _require_columns(
        experiments,
        [
            "experiment_id",
            "oil_id",
            "dispersion_kind",
            "nozzle_diameter",
            "has_gas",
            "measured_d50",
            "oil_flow",
            "gas_flow",
            "oil_density",
            "gas_density",
            "oil_viscosity",
            "water_flow",
            "water_nozzle_diameter",
        ],
        source="Experiments database",
    )

    treated = experiments.loc[experiments["dispersion_kind"].eq("SSMD")].copy()

    if treated.empty:
        raise ValueError("No SSMD experiments were found in the normalized database.")

    untreated = _build_untreated_reference_table(
        experiments,
    )

    dataset = treated.merge(
        untreated,
        on=PAIR_KEYS,
        how="left",
        validate="many_to_one",
    )

    missing_reference = dataset["untreated_experiment_id"].isna()

    if missing_reference.any():
        missing = dataset.loc[
            missing_reference,
            [
                "experiment_id",
                "oil_id",
                "nozzle_diameter",
                "has_gas",
            ],
        ]

        raise ValueError(
            "Untreated reference not found for some SSMD experiments:\n"
            f"{missing.to_string(index=False)}"
        )

    missing_d50 = dataset["untreated_d50_measured"].isna()

    if missing_d50.any():
        missing = dataset.loc[
            missing_d50,
            [
                "oil_id",
                "nozzle_diameter",
                "has_gas",
                "untreated_experiment_id",
            ],
        ]

        raise ValueError(
            "Measured untreated D50 is missing for some SSMD references:\n"
            f"{missing.to_string(index=False)}"
        )

    return dataset.reset_index(drop=True)


def load_ssdi_untreated_predictions(
    *,
    model_version: str,
) -> pd.DataFrame:
    predictions = pd.read_excel(
        paths.SSDI_PREDICTIONS_PATH,
    )

    _require_columns(
        predictions,
        [
            "experiment_id",
            "model_version",
            "d50_pred",
        ],
        source="SSDI predictions",
    )

    selected = predictions.loc[
        predictions["model_version"].eq(model_version),
        [
            "experiment_id",
            "d50_pred",
        ],
    ].copy()

    if selected.empty:
        raise ValueError(
            "No SSDI predictions found for model version " f"{model_version!r}."
        )

    duplicated = selected.duplicated(
        subset=[
            "experiment_id",
        ],
        keep=False,
    )

    if duplicated.any():
        duplicated_rows = selected.loc[
            duplicated,
            [
                "experiment_id",
                "d50_pred",
            ],
        ]

        raise ValueError(
            "Multiple SSDI predictions found for the same experiment "
            f"under model version {model_version!r}:\n"
            f"{duplicated_rows.to_string(index=False)}"
        )

    d50_pred = selected["d50_pred"].to_numpy(
        dtype=float,
    )

    invalid_prediction = ~np.isfinite(d50_pred) | (d50_pred <= 0.0)

    if invalid_prediction.any():
        invalid = selected.loc[
            invalid_prediction,
            [
                "experiment_id",
                "d50_pred",
            ],
        ]

        raise ValueError(
            "Invalid SSDI D50 predictions found for model version "
            f"{model_version!r}:\n"
            f"{invalid.to_string(index=False)}"
        )

    return selected.rename(
        columns={
            "experiment_id": "untreated_experiment_id",
            "d50_pred": "untreated_d50_pred",
        }
    ).reset_index(drop=True)


def add_ssdi_untreated_predictions(
    dataset: pd.DataFrame,
    *,
    model_version: str,
) -> pd.DataFrame:
    _require_columns(
        dataset,
        [
            "untreated_experiment_id",
        ],
        source="SSMD dataset",
    )

    protected_columns = [
        "untreated_d50_pred",
        "ssdi_source_version",
    ]

    existing = [column for column in protected_columns if column in dataset.columns]

    if existing:
        raise ValueError(
            "SSMD dataset already contains SSDI prediction fields: " f"{existing}"
        )

    predictions = load_ssdi_untreated_predictions(
        model_version=model_version,
    )

    required_ids = set(dataset["untreated_experiment_id"].dropna().unique())

    predictions = predictions.loc[
        predictions["untreated_experiment_id"].isin(required_ids)
    ].copy()

    result = dataset.merge(
        predictions,
        on="untreated_experiment_id",
        how="left",
        validate="many_to_one",
    )

    missing_prediction = result["untreated_d50_pred"].isna()

    if missing_prediction.any():
        missing = result.loc[
            missing_prediction,
            [
                "experiment_id",
                "oil_id",
                "nozzle_diameter",
                "has_gas",
                "untreated_experiment_id",
            ],
        ]

        raise ValueError(
            "SSDI prediction missing for some untreated SSMD references "
            f"under model version {model_version!r}:\n"
            f"{missing.to_string(index=False)}"
        )

    result["ssdi_source_version"] = model_version

    return result.reset_index(drop=True)
