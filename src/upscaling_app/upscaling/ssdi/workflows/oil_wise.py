import pandas as pd

from upscaling_app.upscaling.ssdi.calibration.pipeline import (
    calibrate_ssdi_oil_wise,
)
from upscaling_app.upscaling.ssdi.datasets import (
    SSDI_DISPERSION_KINDS,
    SSDI_NOZZLE_DIAMETERS,
    SSDI_OIL_IDS,
)
from upscaling_app.upscaling.ssdi.io.data import (
    load_ssdi_experiments,
)
from upscaling_app.upscaling.ssdi.io.persistence import (
    save_ssdi_calibrations,
    save_ssdi_results,
)
from upscaling_app.upscaling.ssdi.physics.derived_properties import (
    add_ssdi_physics,
)
from upscaling_app.upscaling.ssdi.prediction import (
    predict_ssdi,
)
from upscaling_app.upscaling.ssdi.versions import (
    OIL_WISE_VERSION,
)


def run_oil_wise() -> pd.DataFrame:
    experiments = load_ssdi_experiments(
        oil_ids=SSDI_OIL_IDS,
        nozzle_diameters=SSDI_NOZZLE_DIAMETERS,
        dispersion_kinds=SSDI_DISPERSION_KINDS,
    )

    experiments = add_ssdi_physics(
        experiments,
    )

    calibration_rows = []
    prediction_frames = []

    for oil_id, oil_experiments in experiments.groupby(
        "oil_id",
        sort=True,
    ):
        oil_experiments = oil_experiments.copy()

        calibration = calibrate_ssdi_oil_wise(
            oil_experiments,
        )

        predictions = predict_ssdi(
            experiments=oil_experiments,
            we=calibration.we,
            ca=calibration.ca,
            a=calibration.a_optimized,
            b=calibration.b_optimized,
            model_version=OIL_WISE_VERSION,
            solver="newton",
        )

        prediction_frames.append(
            predictions,
        )

        calibration_rows.append(
            {
                "model_version": OIL_WISE_VERSION,
                "calibration_scope": "oil_wise",
                "oil_id": oil_id,
                "experiment_count": len(oil_experiments),
                "solver": "newton",
                "optimizer": "least_squares",
                "a_initial": calibration.a_initial,
                "b_initial": calibration.b_initial,
                "a_optimized": calibration.a_optimized,
                "b_optimized": calibration.b_optimized,
                "log_mse": calibration.loss,
            }
        )

    predictions = pd.concat(
        prediction_frames,
        ignore_index=True,
    )

    calibrations = (
        pd.DataFrame(calibration_rows).sort_values("oil_id").reset_index(drop=True)
    )

    save_ssdi_results(
        predictions,
    )

    save_ssdi_calibrations(
        calibrations,
    )

    return calibrations
