from __future__ import annotations

import numpy as np
import pandas as pd

MOMENTUM_EXPONENT = -3.0 / 5.0

SINTEF_ETA_NO_GAS = 0.85
SINTEF_ETA_GAS = 0.6779545878291601

SINTEF_C_3MM_NO_GAS = 0.33063475973887657
SINTEF_C_2MM_NO_GAS = 0.46170083447858073
SINTEF_C_2MM_GAS = 0.5720125321034614

SINTEF_D_COEF = 0.05


def _require_columns(
    data: pd.DataFrame,
    columns: list[str],
    *,
    source: str,
) -> None:
    missing = [column for column in columns if column not in data.columns]

    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def momentum_response(
    eta: np.ndarray | pd.Series | float,
    momentum_amplification: np.ndarray | pd.Series | float,
) -> np.ndarray:
    eta_array = np.asarray(
        eta,
        dtype=float,
    )

    amplification_array = np.asarray(
        momentum_amplification,
        dtype=float,
    )

    invalid = (
        ~np.isfinite(eta_array)
        | ~np.isfinite(amplification_array)
        | (eta_array <= 0.0)
        | (amplification_array <= 0.0)
    )

    if np.any(invalid):
        raise ValueError(
            "SSMD momentum response requires finite positive "
            "eta and momentum amplification."
        )

    return (eta_array * amplification_array) ** MOMENTUM_EXPONENT


def oil_property_factor(
    c_coef: np.ndarray | pd.Series | float,
    d_coef: np.ndarray | pd.Series | float,
    oil_viscosity: np.ndarray | pd.Series | float,
    interfacial_tension: np.ndarray | pd.Series | float,
) -> np.ndarray:
    c_array = np.asarray(
        c_coef,
        dtype=float,
    )

    d_array = np.asarray(
        d_coef,
        dtype=float,
    )

    viscosity_array = np.asarray(
        oil_viscosity,
        dtype=float,
    )

    ift_array = np.asarray(
        interfacial_tension,
        dtype=float,
    )

    invalid = (
        ~np.isfinite(c_array)
        | ~np.isfinite(d_array)
        | ~np.isfinite(viscosity_array)
        | ~np.isfinite(ift_array)
        | (viscosity_array < 0.0)
        | (ift_array <= 0.0)
    )

    if np.any(invalid):
        raise ValueError(
            "SSMD oil-property correction requires finite coefficients, "
            "non-negative viscosity, and positive interfacial tension."
        )

    factor = c_array + d_array * viscosity_array / ift_array

    if ~np.all(np.isfinite(factor)) or np.any(factor <= 0.0):
        raise ValueError(
            "SSMD oil-property correction produced "
            "non-positive or non-finite values."
        )

    return factor


def predict_dR(
    *,
    eta: np.ndarray | pd.Series | float,
    momentum_amplification: np.ndarray | pd.Series | float,
    c_coef: np.ndarray | pd.Series | float,
    d_coef: np.ndarray | pd.Series | float,
    oil_viscosity: np.ndarray | pd.Series | float,
    interfacial_tension: np.ndarray | pd.Series | float,
) -> np.ndarray:
    momentum = momentum_response(
        eta=eta,
        momentum_amplification=momentum_amplification,
    )

    property_factor = oil_property_factor(
        c_coef=c_coef,
        d_coef=d_coef,
        oil_viscosity=oil_viscosity,
        interfacial_tension=interfacial_tension,
    )

    prediction = momentum * property_factor

    if ~np.all(np.isfinite(prediction)) or np.any(prediction <= 0.0):
        raise ValueError("SSMD model produced non-positive or non-finite dR values.")

    return prediction


def predict_dR_from_factor(
    *,
    eta: np.ndarray | pd.Series | float,
    momentum_amplification: np.ndarray | pd.Series | float,
    property_factor: np.ndarray | pd.Series | float,
) -> np.ndarray:
    factor_array = np.asarray(
        property_factor,
        dtype=float,
    )

    if ~np.all(np.isfinite(factor_array)) or np.any(factor_array <= 0.0):
        raise ValueError("Oil-wise SSMD property factors must be finite and positive.")

    prediction = (
        momentum_response(
            eta=eta,
            momentum_amplification=momentum_amplification,
        )
        * factor_array
    )

    if ~np.all(np.isfinite(prediction)) or np.any(prediction <= 0.0):
        raise ValueError(
            "Oil-wise SSMD model produced " "non-positive or non-finite dR values."
        )

    return prediction


def add_sintef_eta(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        dataset,
        [
            "has_gas",
        ],
        source="SSMD dataset",
    )

    result = dataset.copy()

    result["eta"] = np.where(
        result["has_gas"].astype(bool),
        SINTEF_ETA_GAS,
        SINTEF_ETA_NO_GAS,
    )

    return result


def add_sintef_parameters(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        dataset,
        [
            "nozzle_diameter",
            "has_gas",
        ],
        source="SSMD dataset",
    )

    result = add_sintef_eta(
        dataset,
    )

    nozzle_diameter = result["nozzle_diameter"].to_numpy(
        dtype=float,
    )

    has_gas = result["has_gas"].astype(bool).to_numpy()

    is_3mm_no_gas = (
        np.isclose(
            nozzle_diameter,
            0.003,
        )
        & ~has_gas
    )

    is_2mm_no_gas = (
        np.isclose(
            nozzle_diameter,
            0.002,
        )
        & ~has_gas
    )

    is_2mm_gas = (
        np.isclose(
            nozzle_diameter,
            0.002,
        )
        & has_gas
    )

    result["c_coef"] = np.select(
        [
            is_3mm_no_gas,
            is_2mm_no_gas,
            is_2mm_gas,
        ],
        [
            SINTEF_C_3MM_NO_GAS,
            SINTEF_C_2MM_NO_GAS,
            SINTEF_C_2MM_GAS,
        ],
        default=np.nan,
    )

    result["d_coef"] = SINTEF_D_COEF

    unsupported = result["c_coef"].isna()

    if unsupported.any():
        columns = [
            "nozzle_diameter",
            "has_gas",
        ]

        if "experiment_id" in result.columns:
            columns.insert(
                0,
                "experiment_id",
            )

        invalid = result.loc[
            unsupported,
            columns,
        ]

        raise ValueError(
            "SINTEF SSMD parameters are not defined for some "
            "experimental regimes:\n"
            f"{invalid.to_string(index=False)}"
        )

    return result


def add_sintef_dR_prediction(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        dataset,
        [
            "momentum_amplification",
            "oil_viscosity",
            "untreated_ift",
        ],
        source="SSMD dataset",
    )

    result = add_sintef_parameters(
        dataset,
    )

    result["dR_pred"] = predict_dR(
        eta=result["eta"],
        momentum_amplification=result["momentum_amplification"],
        c_coef=result["c_coef"],
        d_coef=result["d_coef"],
        oil_viscosity=result["oil_viscosity"],
        interfacial_tension=result["untreated_ift"],
    )

    return result
