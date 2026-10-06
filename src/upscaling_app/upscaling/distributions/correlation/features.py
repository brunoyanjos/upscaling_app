from __future__ import annotations

import numpy as np
import pandas as pd

from upscaling_app.upscaling.distributions.correlation.data import (
    load_distribution_correlation_dataset,
)
from upscaling_app.upscaling.ssdi.physics.derived_properties import (
    add_ssdi_physics,
)
from upscaling_app.upscaling.ssmd.io.data import (
    load_ssmd_calibration_dataset,
)
from upscaling_app.upscaling.ssmd.physics.derived_properties import (
    add_momentum_properties,
    add_untreated_hydrodynamics,
    add_water_jet_properties,
)

RELEASE_FEATURE_COLUMNS = [
    "void_fraction",
    "mixed_density",
    "volumetric_velocity",
    "modified_velocity",
    "reduced_gravity",
    "froude",
    "effective_velocity",
    "reynolds",
    "weber",
    "capillary",
]


SSMD_FEATURE_COLUMNS = [
    "untreated_ift",
    "untreated_gas_void_fraction",
    "untreated_mixed_density",
    "untreated_volumetric_velocity",
    "untreated_modified_velocity",
    "untreated_reduced_gravity",
    "untreated_froude",
    "untreated_effective_velocity",
    "water_velocity",
    "water_momentum_flux",
    "water_kinetic_power",
    "oil_momentum_flux",
    "momentum_amplification",
    "oil_kinetic_power",
    "kinetic_power_ratio",
]


def _require_columns(
    data: pd.DataFrame,
    columns: list[str],
    *,
    source: str,
) -> None:
    missing = [column for column in columns if column not in data.columns]

    if missing:
        raise ValueError(f"{source} is missing required columns: " f"{missing}")


def add_release_physics(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add release hydrodynamics shared by all experimental
    mechanisms.

    These quantities are evaluated from experiment-level
    operating conditions and do not depend on D50 or on the
    fitted Rosin-Rammler parameters.
    """

    result = add_ssdi_physics(data)

    _require_columns(
        result,
        RELEASE_FEATURE_COLUMNS,
        source="Release physics",
    )

    return result


def build_ssmd_feature_table() -> pd.DataFrame:
    """
    Build SSMD-specific physical features.

    The individual SSMD physics functions are called explicitly
    instead of add_derived_properties() so that dR_measured is
    never introduced into the k-correlation feature table.
    """

    dataset = load_ssmd_calibration_dataset()

    dataset = add_untreated_hydrodynamics(dataset)

    dataset = add_water_jet_properties(dataset)

    dataset = add_momentum_properties(dataset)

    _require_columns(
        dataset,
        [
            "experiment_id",
            *SSMD_FEATURE_COLUMNS,
        ],
        source="SSMD physics",
    )

    duplicated = dataset.duplicated(
        subset=["experiment_id"],
        keep=False,
    )

    if duplicated.any():
        duplicates = dataset.loc[
            duplicated,
            [
                "experiment_id",
                "oil_id",
                "dispersion_tag",
            ],
        ]

        raise ValueError(
            "Multiple SSMD feature rows found for the "
            "same experiment_id:\n"
            f"{duplicates.to_string(index=False)}"
        )

    return (
        dataset[
            [
                "experiment_id",
                *SSMD_FEATURE_COLUMNS,
            ]
        ]
        .copy()
        .reset_index(drop=True)
    )


def _validate_finite_features(
    data: pd.DataFrame,
    columns: list[str],
    *,
    source: str,
) -> None:
    values = data[columns].to_numpy(dtype=float)

    invalid = ~np.isfinite(values)

    if invalid.any():
        row_index, column_index = np.where(invalid)

        problems = pd.DataFrame(
            {
                "experiment_id": data.iloc[row_index]["experiment_id"].to_numpy(),
                "column": [columns[index] for index in column_index],
            }
        )

        raise ValueError(
            f"Invalid values found in {source}:\n" f"{problems.to_string(index=False)}"
        )


def build_distribution_correlation_features() -> pd.DataFrame:
    dataset = load_distribution_correlation_dataset()

    # ---------------------------------------------------------
    # Shared release physics
    #
    # Untreated + SSDI + SSMD
    # ---------------------------------------------------------

    dataset = add_release_physics(dataset)

    _validate_finite_features(
        dataset,
        RELEASE_FEATURE_COLUMNS,
        source="release features",
    )

    # ---------------------------------------------------------
    # SSMD-specific physics
    # ---------------------------------------------------------

    ssmd_features = build_ssmd_feature_table()

    dataset = dataset.merge(
        ssmd_features,
        on="experiment_id",
        how="left",
        validate="one_to_one",
    )

    # Every SSMD experiment must have its specific physics.
    ssmd_mask = dataset["dispersion_kind"].eq("SSMD")

    missing_ssmd = (
        dataset.loc[
            ssmd_mask,
            SSMD_FEATURE_COLUMNS,
        ]
        .isna()
        .any(axis=1)
    )

    if missing_ssmd.any():
        missing = dataset.loc[ssmd_mask].loc[
            missing_ssmd,
            [
                "experiment_id",
                "oil_id",
                "dispersion_tag",
                "nozzle_diameter",
                "has_gas",
            ],
        ]

        raise ValueError(
            "SSMD-specific physical features are missing "
            "for some experiments:\n"
            f"{missing.to_string(index=False)}"
        )

    _validate_finite_features(
        dataset.loc[ssmd_mask],
        SSMD_FEATURE_COLUMNS,
        source="SSMD features",
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
