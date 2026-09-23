from __future__ import annotations

import numpy as np
import pandas as pd


def add_point_metrics(
    results: pd.DataFrame,
) -> pd.DataFrame:
    result = results.copy()

    result["absolute_percentage_error"] = (
        np.abs(result["dR_exp"] - result["dR_pred"]) / result["dR_exp"] * 100.0
    )

    result["log_residual"] = np.log(result["dR_exp"]) - np.log(result["dR_pred"])

    return result


def calculate_global_metrics(
    results: pd.DataFrame,
) -> dict[str, float]:
    dR_exp = results["dR_exp"].to_numpy()
    dR_pred = results["dR_pred"].to_numpy()

    residual = dR_exp - dR_pred

    ss_res = np.sum(residual**2)
    ss_tot = np.sum((dR_exp - np.mean(dR_exp)) ** 2)

    r2 = 1.0 - ss_res / ss_tot

    rmse = np.sqrt(np.mean(residual**2))

    mape = np.mean(np.abs(residual / dR_exp)) * 100.0

    log_residual = np.log(dR_exp) - np.log(dR_pred)

    log_mse = np.mean(log_residual**2)

    return {
        "log_mse": float(log_mse),
        "r2": float(r2),
        "rmse": float(rmse),
        "mape": float(mape),
        "mean_log_residual": float(np.mean(log_residual)),
        "std_log_residual": float(
            np.std(
                log_residual,
                ddof=1,
            )
        ),
    }
