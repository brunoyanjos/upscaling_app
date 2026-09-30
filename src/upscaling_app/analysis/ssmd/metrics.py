from __future__ import annotations

import numpy as np


def validate_predictions(
    observed: np.ndarray,
    predicted: np.ndarray,
) -> None:
    if observed.ndim != 1 or predicted.ndim != 1:
        raise ValueError("Observed and predicted arrays must be one-dimensional.")

    if len(observed) != len(predicted):
        raise ValueError("Observed and predicted arrays must have the same length.")

    if len(observed) == 0:
        raise ValueError("Performance evaluation requires at least one observation.")

    invalid = (
        ~np.isfinite(observed)
        | ~np.isfinite(predicted)
        | (observed <= 0.0)
        | (predicted <= 0.0)
    )

    if invalid.any():
        raise ValueError("Performance evaluation requires finite positive values.")


def calculate_metrics(
    observed: np.ndarray,
    predicted: np.ndarray,
) -> dict[str, float | int]:
    validate_predictions(
        observed,
        predicted,
    )

    log_observed = np.log(observed)

    log_predicted = np.log(predicted)

    log_residual = log_observed - log_predicted

    log_mse = float(np.mean(log_residual**2))

    ss_res = float(np.sum(log_residual**2))

    ss_tot = float(np.sum((log_observed - np.mean(log_observed)) ** 2))

    r2_log = 1.0 - ss_res / ss_tot if ss_tot > 0.0 else np.nan

    rmse = float(np.sqrt(np.mean((observed - predicted) ** 2)))

    mape = float(100.0 * np.mean(np.abs((observed - predicted) / observed)))

    return {
        "n": len(observed),
        "log_mse": log_mse,
        "r2_log": float(r2_log),
        "rmse": rmse,
        "mape_pct": mape,
        "mean_log_residual": float(np.mean(log_residual)),
        "std_log_residual": (
            float(
                np.std(
                    log_residual,
                    ddof=1,
                )
            )
            if len(log_residual) > 1
            else 0.0
        ),
    }
