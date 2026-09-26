from __future__ import annotations

import numpy as np
import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.experimental.data import (
    load_experiments,
)
from upscaling_app.analysis.experimental.ssmd.analysis import (
    prepare_ssmd_experimental_data,
)
from upscaling_app.analysis.ssmd.plotting import (
    save_ssmd_parity_plot,
)
from upscaling_app.upscaling.ssmd.versions import (
    REGRESSED_CD_GLOBAL,
    SINTEF_BASELINE,
)

ETA_NO_GAS = 0.85
ETA_GAS = 0.68

EQ5_REFERENCE = "eq5_reference"


def build_eq5_reference_predictions(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build Equation-5 SSMD reference predictions:

        dR = (eta * A_M)^(-3/5)
    """

    eq5 = data.copy()

    eq5["eta_reference"] = eq5["has_gas"].map(
        {
            False: ETA_NO_GAS,
            True: ETA_GAS,
        }
    )

    eq5["dR_exp"] = eq5["dR_measured"]

    eq5["dR_pred"] = (eq5["eta_reference"] * eq5["momentum_amplification"]) ** (
        -3.0 / 5.0
    )

    eq5["model_version"] = EQ5_REFERENCE

    return eq5[
        [
            "experiment_id",
            "oil_id",
            "regime",
            "has_gas",
            "dR_exp",
            "dR_pred",
            "model_version",
        ]
    ].reset_index(drop=True)


def add_ssmd_metadata(
    predictions: pd.DataFrame,
    ssmd_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add experimental metadata required by the analysis layer
    to persisted SSMD prediction results.
    """

    metadata = (
        ssmd_data[
            [
                "experiment_id",
                "oil_id",
                "regime",
                "has_gas",
            ]
        ]
        .drop_duplicates(subset="experiment_id")
        .reset_index(drop=True)
    )

    missing_columns = [
        column
        for column in [
            "oil_id",
            "regime",
            "has_gas",
        ]
        if column not in predictions.columns
    ]

    if not missing_columns:
        return predictions.copy()

    enriched = predictions.merge(
        metadata[
            [
                "experiment_id",
                *missing_columns,
            ]
        ],
        on="experiment_id",
        how="left",
        validate="many_to_one",
    )

    if enriched[missing_columns].isna().any().any():
        raise ValueError(
            "Some persisted SSMD predictions could not "
            "be matched with experimental metadata."
        )

    return enriched


def build_shared_limits(
    data: pd.DataFrame,
) -> tuple[float, float]:
    values = np.concatenate(
        [
            data["dR_exp"].to_numpy(),
            data["dR_pred"].to_numpy(),
        ]
    )

    values = values[np.isfinite(values) & (values > 0.0)]

    minimum = values.min()
    maximum = values.max()

    return (
        minimum * 0.90,
        maximum * 1.10,
    )


def run_ssmd_analysis() -> None:
    # ========================================================
    # Persisted model results
    # ========================================================

    predictions = pd.read_excel(paths.SSMD_RESULTS)

    # ========================================================
    # Experimental SSMD metadata / physics
    # ========================================================

    experiments = load_experiments()

    ssmd_data = prepare_ssmd_experimental_data(experiments)

    # Add regime / gas metadata to persisted predictions.
    predictions = add_ssmd_metadata(
        predictions,
        ssmd_data,
    )

    # ========================================================
    # Equation 5 reference
    # ========================================================

    eq5_predictions = build_eq5_reference_predictions(ssmd_data)

    # ========================================================
    # Models used in the comparison
    # ========================================================

    selected_predictions = predictions.loc[
        predictions["model_version"].isin(
            [
                SINTEF_BASELINE,
                REGRESSED_CD_GLOBAL,
            ]
        ),
        [
            "experiment_id",
            "oil_id",
            "regime",
            "has_gas",
            "dR_exp",
            "dR_pred",
            "model_version",
        ],
    ].copy()

    comparison = pd.concat(
        [
            eq5_predictions,
            selected_predictions,
        ],
        ignore_index=True,
    )

    # ========================================================
    # Common parity limits
    # ========================================================

    limits = build_shared_limits(comparison)

    # ========================================================
    # Output
    # ========================================================

    output_dir = paths.RESULTS_DIR / "analysis" / "ssmd" / "figures"

    save_ssmd_parity_plot(
        comparison,
        model_version=EQ5_REFERENCE,
        limits=limits,
        output=(output_dir / "ssmd_parity_eq5.png"),
    )

    save_ssmd_parity_plot(
        comparison,
        model_version=SINTEF_BASELINE,
        limits=limits,
        output=(output_dir / "ssmd_parity_sintef.png"),
    )

    save_ssmd_parity_plot(
        comparison,
        model_version=REGRESSED_CD_GLOBAL,
        limits=limits,
        output=(output_dir / "ssmd_parity_regressed_cd_global.png"),
    )
