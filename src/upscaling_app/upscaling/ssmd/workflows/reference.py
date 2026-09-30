from __future__ import annotations

import pandas as pd

from upscaling_app.upscaling.ssdi.versions import (
    BASELINE_VERSION as DEFAULT_SSDI_SOURCE_VERSION,
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
    add_sintef_dR_prediction,
)
from upscaling_app.upscaling.ssmd.prediction import (
    add_end_to_end_prediction,
    build_prediction_table,
)
from upscaling_app.upscaling.ssmd.versions import (
    SINTEF_REFERENCE_VERSION,
)


def run_reference(
    *,
    ssdi_source_version: str = DEFAULT_SSDI_SOURCE_VERSION,
) -> pd.DataFrame:
    dataset = load_ssmd_calibration_dataset()

    dataset = add_derived_properties(
        dataset,
    )

    dataset = add_sintef_dR_prediction(
        dataset,
    )

    dataset = add_end_to_end_prediction(
        dataset,
        ssdi_source_version=ssdi_source_version,
    )

    predictions = build_prediction_table(
        dataset,
        ssmd_model_version=SINTEF_REFERENCE_VERSION,
    )

    save_predictions(
        predictions,
    )

    return predictions
