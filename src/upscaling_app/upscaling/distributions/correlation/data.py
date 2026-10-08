from __future__ import annotations

import numpy as np
import pandas as pd

from upscaling_app import paths
from upscaling_app.upscaling.distributions.persistence import (
    load_distribution_parameters as load_fitted_distribution_parameters,
)

EXPERIMENT_COLUMNS = [
    "experiment_id",
    "oil_id",
    "dispersion_kind",
    "dispersion_tag",
    "nozzle_diameter",
    "has_gas",
    "ift",
    "oil_flow",
    "gas_flow",
    "oil_viscosity",
    "oil_density",
    "gas_density",
    "water_jet_fraction",
    "water_flow",
    "water_nozzle_diameter",
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


def load_distribution_parameters() -> pd.DataFrame:
    parameters = load_fitted_distribution_parameters()

    shape = parameters["shape"].to_numpy(dtype=float)
    invalid_shape = ~np.isfinite(shape) | (shape <= 0.0)

    if invalid_shape.any():
        invalid = parameters.loc[
            invalid_shape,
            ["experiment_id", "shape"],
        ]

        raise ValueError(
            "Invalid Rosin-Rammler shape parameters:\n"
            f"{invalid.to_string(index=False)}"
        )

    return parameters[["experiment_id", "shape"]].copy().reset_index(drop=True)


def load_correlation_experiments() -> pd.DataFrame:
    experiments = pd.read_excel(paths.EXPERIMENTS_DATABASE)

    _require_columns(
        experiments,
        EXPERIMENT_COLUMNS,
        source="Experiments database",
    )

    duplicated = experiments.duplicated(
        subset=["experiment_id"],
        keep=False,
    )

    if duplicated.any():
        duplicates = experiments.loc[
            duplicated,
            [
                "experiment_id",
                "oil_id",
                "dispersion_kind",
                "dispersion_tag",
            ],
        ]

        raise ValueError(
            "Multiple experiment rows found for the same experiment_id:\n"
            f"{duplicates.to_string(index=False)}"
        )

    return experiments[EXPERIMENT_COLUMNS].copy().reset_index(drop=True)


def load_distribution_correlation_dataset() -> pd.DataFrame:
    parameters = load_distribution_parameters()
    experiments = load_correlation_experiments()

    dataset = parameters.merge(
        experiments,
        on="experiment_id",
        how="left",
        validate="one_to_one",
    )

    missing_experiment = dataset["oil_id"].isna()

    if missing_experiment.any():
        missing = dataset.loc[
            missing_experiment,
            ["experiment_id", "shape"],
        ]

        raise ValueError(
            "Distribution parameters could not be linked "
            "to normalized experiments:\n"
            f"{missing.to_string(index=False)}"
        )

    return dataset.sort_values(
        [
            "dispersion_kind",
            "dispersion_tag",
            "oil_id",
            "nozzle_diameter",
            "has_gas",
        ]
    ).reset_index(drop=True)
