from __future__ import annotations

import numpy as np
import pandas as pd

from upscaling_app.upscaling.ssmd.physics.model import (
    add_sintef_eta,
    momentum_response,
)


def _require_columns(
    data: pd.DataFrame,
    columns: list[str],
    *,
    source: str,
) -> None:
    missing = [column for column in columns if column not in data.columns]

    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def _prepare_regression_data(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        dataset,
        [
            "oil_id",
            "has_gas",
            "momentum_amplification",
            "oil_viscosity",
            "untreated_ift",
            "dR_measured",
        ],
        source="SSMD calibration dataset",
    )

    return add_sintef_eta(
        dataset,
    )


def _build_regression_arrays(
    dataset: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    momentum = momentum_response(
        eta=dataset["eta"],
        momentum_amplification=dataset["momentum_amplification"],
    )

    x = (dataset["oil_viscosity"] / dataset["untreated_ift"]).to_numpy(
        dtype=float,
    )

    y = (
        dataset["dR_measured"].to_numpy(
            dtype=float,
        )
        / momentum
    )

    invalid = ~np.isfinite(x) | ~np.isfinite(y)

    if invalid.any():
        raise ValueError("Non-finite values found in the SSMD regression variables.")

    return x, y


def _fit_linear_cd(
    x: np.ndarray,
    y: np.ndarray,
) -> tuple[float, float]:
    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("SSMD regression arrays must be one-dimensional.")

    if len(x) != len(y):
        raise ValueError("SSMD regression arrays must have the same length.")

    if len(x) < 2:
        raise ValueError("At least two observations are required to fit global c,d.")

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

    if not (np.isfinite(c_coef) and np.isfinite(d_coef)):
        raise ValueError("SSMD global regression produced non-finite coefficients.")

    fitted_factor = c_coef + d_coef * x

    if ~np.all(np.isfinite(fitted_factor)) or np.any(fitted_factor <= 0.0):
        raise ValueError(
            "SSMD global regression produced a non-positive property factor."
        )

    return (
        float(c_coef),
        float(d_coef),
    )


def fit_cd_global(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    data = _prepare_regression_data(
        dataset,
    )

    x, y = _build_regression_arrays(
        data,
    )

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
    data = _prepare_regression_data(
        dataset,
    )

    momentum = momentum_response(
        eta=data["eta"],
        momentum_amplification=data["momentum_amplification"],
    )

    local_response = (
        data["dR_measured"].to_numpy(
            dtype=float,
        )
        / momentum
    )

    if ~np.all(np.isfinite(local_response)) or np.any(local_response <= 0.0):
        raise ValueError("Invalid local SSMD response found during oil-wise fitting.")

    prepared = data.assign(
        local_response=local_response,
    )

    rows: list[dict[str, object]] = []

    for oil_id, group in prepared.groupby(
        "oil_id",
        sort=True,
    ):
        values = group["local_response"].to_numpy(
            dtype=float,
        )

        k_coef = float(np.mean(values))

        k_std = (
            float(
                np.std(
                    values,
                    ddof=1,
                )
            )
            if len(values) > 1
            else 0.0
        )

        rows.append(
            {
                "oil_id": oil_id,
                "k_coef": k_coef,
                "k_std": k_std,
                "n_experiments": len(group),
            }
        )

    result = pd.DataFrame(
        rows,
    )

    if result.empty:
        raise ValueError("No oil-wise SSMD factors were fitted.")

    return result
