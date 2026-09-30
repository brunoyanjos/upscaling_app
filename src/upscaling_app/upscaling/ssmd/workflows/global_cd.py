from __future__ import annotations

import pandas as pd

from upscaling_app.upscaling.ssdi.versions import (
    BASELINE_VERSION as DEFAULT_SSDI_SOURCE_VERSION,
)
from upscaling_app.upscaling.ssmd.calibration.regression import (
    fit_cd_global,
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
    add_end_to_end_prediction,
    add_global_cd_prediction,
    build_prediction_table,
)
from upscaling_app.upscaling.ssmd.versions import (
    GLOBAL_CD_VERSION,
)


def _prepare_dataset() -> pd.DataFrame:
    dataset = load_ssmd_calibration_dataset()

    return add_derived_properties(
        dataset,
    )


def calibrate_global() -> pd.DataFrame:
    dataset = _prepare_dataset()

    calibration = fit_cd_global(
        dataset,
    )

    calibration.insert(
        0,
        "ssmd_model_version",
        GLOBAL_CD_VERSION,
    )

    save_calibrations(
        calibration,
    )

    return calibration


def run_global(
    *,
    ssdi_source_version: str = DEFAULT_SSDI_SOURCE_VERSION,
) -> pd.DataFrame:
    dataset = _prepare_dataset()

    calibration = fit_cd_global(
        dataset,
    )

    calibration.insert(
        0,
        "ssmd_model_version",
        GLOBAL_CD_VERSION,
    )

    save_calibrations(
        calibration,
    )

    dataset = add_global_cd_prediction(
        dataset,
        calibration,
    )

    dataset = add_end_to_end_prediction(
        dataset,
        ssdi_source_version=ssdi_source_version,
    )

    predictions = build_prediction_table(
        dataset,
        ssmd_model_version=GLOBAL_CD_VERSION,
    )

    save_predictions(
        predictions,
    )

    return predictions
