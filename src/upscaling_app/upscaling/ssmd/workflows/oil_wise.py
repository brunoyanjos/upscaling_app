from __future__ import annotations

import numpy as np
import pandas as pd

from upscaling_app.upscaling.ssmd.calibration.regression import (
    fit_oil_wise_factor,
)
from upscaling_app.upscaling.ssmd.io.data import (
    load_ssmd_calibration_dataset,
)
from upscaling_app.upscaling.ssmd.io.persistence import (
    save_calibrations,
    save_predictions,
)
from upscaling_app.upscaling.ssmd.physics.derived_properties import (
    add_derived_properties,
)
from upscaling_app.upscaling.ssmd.prediction import (
    add_oil_wise_prediction,
    build_oil_wise_prediction_table,
)
from upscaling_app.upscaling.ssmd.versions import (
    REGRESSED_OIL_WISE,
)


def _log_mse(
    measured: pd.Series,
    predicted: pd.Series,
) -> float:
    residual = np.log(measured) - np.log(predicted)
    return float(np.mean(residual**2))


def run_oil_wise() -> pd.DataFrame:
    dataset = load_ssmd_calibration_dataset()
    dataset = add_derived_properties(dataset)

    coefficients = fit_oil_wise_factor(dataset)

    local = add_oil_wise_prediction(
        dataset,
        coefficients,
    )

    predictions = build_oil_wise_prediction_table(
        local,
        model_version=REGRESSED_OIL_WISE,
    )

    rows = []

    for oil_id, group in local.groupby(
        "oil_id",
        sort=True,
    ):
        k_coef = float(group["k_coef"].iloc[0])

        rows.append(
            {
                "model_version": REGRESSED_OIL_WISE,
                "oil_id": oil_id,
                "n": len(group),
                "regression": "oil_wise_property_factor",
                "k_coef": k_coef,
                "log_mse": _log_mse(
                    group["dR_measured"],
                    group["dR_pred"],
                ),
            }
        )

    calibrations = pd.DataFrame(rows)

    save_predictions(predictions)
    save_calibrations(calibrations)

    return calibrations
