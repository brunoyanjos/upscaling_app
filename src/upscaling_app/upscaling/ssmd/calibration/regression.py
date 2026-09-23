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
