from __future__ import annotations

import numpy as np
import pandas as pd

from upscaling_app.upscaling.ssmd.physics.model import (
    EXPONENT,
    add_sintef_eta,
)

REGIME_KEYS = [
    "nozzle_diameter",
    "has_gas",
]

PREDICTION_COLUMNS = [
    "experiment_id",
    "untreated_experiment_id",
    "eta",
    "c_coef",
    "d_coef",
    "dR_measured",
    "dR_pred",
    "measured_d50",
    "d50_pred",
]


def add_regressed_prediction(
    dataset: pd.DataFrame,
    coefficients: pd.DataFrame,
) -> pd.DataFrame:
    result = dataset.merge(
        coefficients[
            REGIME_KEYS
            + [
                "eta",
                "c_coef",
                "d_coef",
            ]
        ],
        on=REGIME_KEYS,
        how="left",
        validate="many_to_one",
    )

    missing_coefficients = result[["eta", "c_coef", "d_coef"]].isna().any(axis=1)

    if missing_coefficients.any():
        missing = result.loc[
            missing_coefficients,
            [
                "experiment_id",
                "nozzle_diameter",
                "has_gas",
            ],
        ]

        raise ValueError(
            "Regression coefficients missing for some SSMD experiments:\n"
            f"{missing.to_string(index=False)}"
        )

    result["dR_pred"] = (
        result["eta"] * result["momentum_amplification"]
    ) ** EXPONENT * (
        result["c_coef"]
        + result["d_coef"] * result["oil_viscosity"] / result["untreated_ift"]
    )

    result["d50_pred"] = result["dR_pred"] * result["untreated_d50_pred"]

    return result


def add_global_regressed_prediction(
    dataset: pd.DataFrame,
    coefficients: pd.DataFrame,
) -> pd.DataFrame:
    if len(coefficients) != 1:
        raise ValueError(
            "Global SSMD regression must contain exactly one coefficient set."
        )

    result = dataset.copy()

    c_coef = float(coefficients["c_coef"].iloc[0])
    d_coef = float(coefficients["d_coef"].iloc[0])

    result = add_sintef_eta(result)

    result["c_coef"] = c_coef
    result["d_coef"] = d_coef

    result["dR_pred"] = (
        result["eta"] * result["momentum_amplification"]
    ) ** EXPONENT * (
        result["c_coef"]
        + result["d_coef"] * result["oil_viscosity"] / result["untreated_ift"]
    )

    result["d50_pred"] = result["dR_pred"] * result["untreated_d50_pred"]

    return result


def add_oil_wise_prediction(
    dataset: pd.DataFrame,
    coefficients: pd.DataFrame,
) -> pd.DataFrame:
    result = add_sintef_eta(dataset)

    result = result.merge(
        coefficients[
            [
                "oil_id",
                "k_coef",
            ]
        ],
        on="oil_id",
        how="left",
        validate="many_to_one",
    )

    if result["k_coef"].isna().any():
        missing = result.loc[
            result["k_coef"].isna(),
            ["experiment_id", "oil_id"],
        ]
        raise ValueError(
            "Oil-wise SSMD coefficient missing for some experiments:\n"
            f"{missing.to_string(index=False)}"
        )

    result["dR_pred"] = (
        result["eta"]
        * result["momentum_amplification"]
    ) ** EXPONENT * result["k_coef"]

    if (
        ~np.isfinite(result["dR_pred"])
        | (result["dR_pred"] <= 0.0)
    ).any():
        raise ValueError("Oil-wise SSMD prediction produced invalid dR values.")

    result["d50_pred"] = (
        result["dR_pred"]
        * result["untreated_d50_pred"]
    )

    return result


def build_prediction_table(
    dataset: pd.DataFrame,
    *,
    model_version: str,
) -> pd.DataFrame:
    predictions = dataset[PREDICTION_COLUMNS].copy()

    predictions.insert(
        2,
        "model_version",
        model_version,
    )

    return predictions.rename(
        columns={
            "dR_measured": "dR_exp",
            "measured_d50": "d50_exp",
        }
    )


def build_oil_wise_prediction_table(
    dataset: pd.DataFrame,
    *,
    model_version: str,
) -> pd.DataFrame:
    predictions = dataset[
        [
            "experiment_id",
            "untreated_experiment_id",
            "eta",
            "k_coef",
            "dR_measured",
            "dR_pred",
            "measured_d50",
            "d50_pred",
        ]
    ].copy()

    predictions.insert(
        2,
        "model_version",
        model_version,
    )

    # Keep the persisted schema compatible with the existing SSMD results.
    predictions["c_coef"] = np.nan
    predictions["d_coef"] = np.nan

    return predictions.rename(
        columns={
            "dR_measured": "dR_exp",
            "measured_d50": "d50_exp",
        }
    )
