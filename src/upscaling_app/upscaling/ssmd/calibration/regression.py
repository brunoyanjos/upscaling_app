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


def _build_regression_arrays(
    dataset: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    momentum_term = (dataset["eta"] * dataset["momentum_amplification"]) ** EXPONENT

    x = (dataset["oil_viscosity"] / dataset["untreated_ift"]).to_numpy()

    y = (dataset["dR_measured"] / momentum_term).to_numpy()

    return x, y


def _fit_linear_cd(
    x: np.ndarray,
    y: np.ndarray,
) -> tuple[float, float]:
    design_matrix = np.column_stack(
        [
            np.ones_like(x),
            x,
        ]
    )

    coefficients, *_ = np.linalg.lstsq(
        design_matrix,
        y,
        rcond=None,
    )

    c_coef, d_coef = coefficients

    return float(c_coef), float(d_coef)


def fit_cd_by_regime(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    data = add_sintef_eta(dataset)

    rows = []

    for regime, group in data.groupby(
        REGIME_KEYS,
        sort=True,
    ):
        nozzle_diameter, has_gas = regime

        x, y = _build_regression_arrays(group)

        c_coef, d_coef = _fit_linear_cd(
            x,
            y,
        )

        rows.append(
            {
                "nozzle_diameter": nozzle_diameter,
                "has_gas": has_gas,
                "eta": float(group["eta"].iloc[0]),
                "c_coef": c_coef,
                "d_coef": d_coef,
                "n_experiments": len(group),
            }
        )

    return pd.DataFrame(rows)


def fit_cd_global(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    data = add_sintef_eta(dataset)

    x, y = _build_regression_arrays(data)

    c_coef, d_coef = _fit_linear_cd(
        x,
        y,
    )

    return pd.DataFrame(
        [
            {
                "c_coef": c_coef,
                "d_coef": d_coef,
                "n_experiments": len(data),
            }
        ]
    )


def fit_oil_wise_factor(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    """Fit one identifiable SSMD property factor per oil.

    The global Equation-6 regression is

        y = c + d * (mu / sigma)

    with

        y = dR / (eta * A_M)^(-3/5).

    Within one oil, mu/sigma is an oil-level property and does not provide
    independent information to identify both c and d. The identifiable local
    quantity is therefore

        k_oil = c + d * (mu / sigma).

    Least squares for an intercept-only local model gives k_oil = mean(y).
    """
    data = add_sintef_eta(dataset)

    momentum_term = (
        data["eta"]
        * data["momentum_amplification"]
    ) ** EXPONENT

    local_response = (
        data["dR_measured"]
        / momentum_term
    )

    rows = []

    for oil_id, group in data.assign(
        local_response=local_response,
    ).groupby(
        "oil_id",
        sort=True,
    ):
        values = group["local_response"].to_numpy(dtype=float)

        if not np.all(np.isfinite(values)):
            raise ValueError(
                f"Non-finite SSMD local response found for oil {oil_id}."
            )

        rows.append(
            {
                "oil_id": oil_id,
                "k_coef": float(np.mean(values)),
                "k_std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
                "n_experiments": len(group),
            }
        )

    return pd.DataFrame(rows)
