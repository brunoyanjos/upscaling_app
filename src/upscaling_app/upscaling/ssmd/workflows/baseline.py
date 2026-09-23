from __future__ import annotations

import numpy as np
import pandas as pd

from upscaling_app.upscaling.ssmd.calibration.regression import (
    fit_cd_by_regime,
    fit_cd_global,
)
from upscaling_app.upscaling.ssmd.io.data import (
    load_ssmd_calibration_dataset,
)
from upscaling_app.upscaling.ssmd.io.persistence import (
    save_predictions,
)
from upscaling_app.upscaling.ssmd.physics.derived_properties import (
    add_derived_properties,
)
from upscaling_app.upscaling.ssmd.physics.model import (
    add_sintef_prediction,
)
from upscaling_app.upscaling.ssmd.prediction import (
    add_global_regressed_prediction,
    add_regressed_prediction,
    build_prediction_table,
)
from upscaling_app.upscaling.ssmd.results import (
    BaselineResult,
    SSMDModelResult,
    SSMDRegimeResult,
)
from upscaling_app.upscaling.ssmd.versions import (
    REGRESSED_CD_BASELINE,
    REGRESSED_CD_GLOBAL,
    SINTEF_BASELINE,
)


def _log_mse(
    measured: pd.Series,
    predicted: pd.Series,
) -> float:
    residual = np.log(measured) - np.log(predicted)

    return float(np.mean(residual**2))


def _build_model_result(
    dataset: pd.DataFrame,
    model_version: str,
) -> SSMDModelResult:
    regimes = (
        dataset[
            [
                "nozzle_diameter",
                "has_gas",
                "eta",
                "c_coef",
                "d_coef",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            ["nozzle_diameter", "has_gas"],
        )
    )

    regime_results = tuple(
        SSMDRegimeResult(
            nozzle_diameter=float(row.nozzle_diameter),
            has_gas=bool(row.has_gas),
            eta=float(row.eta),
            c_coef=float(row.c_coef),
            d_coef=float(row.d_coef),
        )
        for row in regimes.itertuples(index=False)
    )

    return SSMDModelResult(
        model_version=model_version,
        experiment_count=len(dataset),
        regimes=regime_results,
        loss=_log_mse(
            dataset["dR_measured"],
            dataset["dR_pred"],
        ),
    )


def run_baseline() -> BaselineResult:
    dataset = load_ssmd_calibration_dataset()
    dataset = add_derived_properties(dataset)

    sintef = add_sintef_prediction(dataset)

    regime_coefficients = fit_cd_by_regime(dataset)

    regressed = add_regressed_prediction(
        dataset,
        regime_coefficients,
    )

    global_coefficients = fit_cd_global(dataset)

    global_regressed = add_global_regressed_prediction(
        dataset,
        global_coefficients,
    )

    sintef_predictions = build_prediction_table(
        sintef,
        model_version=SINTEF_BASELINE,
    )

    regressed_predictions = build_prediction_table(
        regressed,
        model_version=REGRESSED_CD_BASELINE,
    )

    global_predictions = build_prediction_table(
        global_regressed,
        model_version=REGRESSED_CD_GLOBAL,
    )

    predictions = pd.concat(
        [
            regressed_predictions,
            global_predictions,
            sintef_predictions,
        ],
        ignore_index=True,
    )

    save_predictions(predictions)

    return BaselineResult(
        model=_build_model_result(
            regressed,
            REGRESSED_CD_BASELINE,
        ),
        global_model=_build_model_result(
            global_regressed,
            REGRESSED_CD_GLOBAL,
        ),
        reference=_build_model_result(
            sintef,
            SINTEF_BASELINE,
        ),
    )
