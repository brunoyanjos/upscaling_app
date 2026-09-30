from __future__ import annotations

import numpy as np
import pandas as pd

from upscaling_app.upscaling.ssmd.io.data import (
    add_ssdi_untreated_predictions,
)
from upscaling_app.upscaling.ssmd.physics.model import (
    add_sintef_parameters,
    predict_dR,
    predict_dR_from_factor,
)

PREDICTION_COLUMNS = [
    "experiment_id",
    "untreated_experiment_id",
    "oil_id",
    "nozzle_diameter",
    "has_gas",
    "water_jet_fraction",
    "ssmd_model_version",
    "ssdi_source_version",
    "eta",
    "c_coef",
    "d_coef",
    "k_coef",
    "momentum_amplification",
    "dR_measured",
    "dR_pred",
    "measured_d50",
    "untreated_d50_measured",
    "untreated_d50_pred",
    "d50_pred",
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


def add_global_cd_prediction(
    dataset: pd.DataFrame,
    coefficients: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        coefficients,
        [
            "c_coef",
            "d_coef",
        ],
        source="Global SSMD calibration",
    )

    if len(coefficients) != 1:
        raise ValueError(
            "Global SSMD calibration must contain exactly one coefficient set."
        )

    result = add_sintef_parameters(
        dataset,
    )

    result["c_coef"] = float(coefficients["c_coef"].iloc[0])

    result["d_coef"] = float(coefficients["d_coef"].iloc[0])

    result["dR_pred"] = predict_dR(
        eta=result["eta"],
        momentum_amplification=result["momentum_amplification"],
        c_coef=result["c_coef"],
        d_coef=result["d_coef"],
        oil_viscosity=result["oil_viscosity"],
        interfacial_tension=result["untreated_ift"],
    )

    return result


def add_oil_wise_factor_prediction(
    dataset: pd.DataFrame,
    coefficients: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        coefficients,
        [
            "oil_id",
            "k_coef",
        ],
        source="Oil-wise SSMD calibration",
    )

    duplicated = coefficients["oil_id"].duplicated(
        keep=False,
    )

    if duplicated.any():
        duplicate_rows = coefficients.loc[
            duplicated,
            [
                "oil_id",
                "k_coef",
            ],
        ]

        raise ValueError(
            "Multiple oil-wise SSMD factors found for the same oil:\n"
            f"{duplicate_rows.to_string(index=False)}"
        )

    result = add_sintef_parameters(
        dataset,
    )

    result = result.drop(
        columns=[
            "c_coef",
            "d_coef",
        ]
    )

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

    missing = result["k_coef"].isna()

    if missing.any():
        missing_rows = result.loc[
            missing,
            [
                "experiment_id",
                "oil_id",
            ],
        ]

        raise ValueError(
            "Oil-wise SSMD factor missing for some experiments:\n"
            f"{missing_rows.to_string(index=False)}"
        )

    result["dR_pred"] = predict_dR_from_factor(
        eta=result["eta"],
        momentum_amplification=result["momentum_amplification"],
        property_factor=result["k_coef"],
    )

    return result


def add_end_to_end_prediction(
    dataset: pd.DataFrame,
    *,
    ssdi_source_version: str,
) -> pd.DataFrame:
    _require_columns(
        dataset,
        [
            "untreated_experiment_id",
            "dR_pred",
        ],
        source="SSMD prediction dataset",
    )

    result = add_ssdi_untreated_predictions(
        dataset,
        model_version=ssdi_source_version,
    )

    result["d50_pred"] = result["dR_pred"] * result["untreated_d50_pred"]

    d50_pred = result["d50_pred"].to_numpy(
        dtype=float,
    )

    invalid = ~np.isfinite(d50_pred) | (d50_pred <= 0.0)

    if invalid.any():
        invalid_rows = result.loc[
            invalid,
            [
                "experiment_id",
                "untreated_experiment_id",
                "dR_pred",
                "untreated_d50_pred",
                "d50_pred",
            ],
        ]

        raise ValueError(
            "Invalid end-to-end SSMD predictions found:\n"
            f"{invalid_rows.to_string(index=False)}"
        )

    return result


def build_prediction_table(
    dataset: pd.DataFrame,
    *,
    ssmd_model_version: str,
) -> pd.DataFrame:
    _require_columns(
        dataset,
        [
            "experiment_id",
            "untreated_experiment_id",
            "oil_id",
            "nozzle_diameter",
            "has_gas",
            "water_jet_fraction",
            "ssdi_source_version",
            "eta",
            "momentum_amplification",
            "dR_measured",
            "dR_pred",
            "measured_d50",
            "untreated_d50_measured",
            "untreated_d50_pred",
            "d50_pred",
        ],
        source="SSMD prediction dataset",
    )

    predictions = dataset.copy()

    if "c_coef" not in predictions.columns:
        predictions["c_coef"] = np.nan

    if "d_coef" not in predictions.columns:
        predictions["d_coef"] = np.nan

    if "k_coef" not in predictions.columns:
        predictions["k_coef"] = np.nan

    predictions["ssmd_model_version"] = ssmd_model_version

    predictions = predictions[PREDICTION_COLUMNS].copy()

    return predictions.rename(
        columns={
            "dR_measured": "dR_exp",
            "measured_d50": "d50_exp",
            "untreated_d50_measured": "untreated_d50_exp",
        }
    )
