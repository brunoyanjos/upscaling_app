import pandas as pd

from upscaling_app import paths
from upscaling_app.upscaling.ssdi.calibration.pipeline import calibrate_ssdi
from upscaling_app.upscaling.ssdi.io.data import load_ssdi_experiments
from upscaling_app.upscaling.ssdi.io.persistence import save_ssdi_results
from upscaling_app.upscaling.ssdi.physics.derived_properties import add_ssdi_physics
from upscaling_app.upscaling.ssdi.prediction import predict_ssdi
from upscaling_app.upscaling.ssdi.results import SSDIModelResult
from upscaling_app.upscaling.ssdi.versions import (
    BASELINE_VERSION,
    FILTERED_VERSION,
)

ALL_OILS = [
    3014,
    3015,
    3016,
    4661,
    4662,
    4663,
    4664,
    4665,
    4666,
    4667,
]


def run_filtered() -> SSDIModelResult:
    analysis_path = paths.RESULTS_DIR / f"ssdi_analysis_{BASELINE_VERSION}.xlsx"

    analysis = pd.read_excel(analysis_path)

    valid_ids = analysis.loc[
        ~analysis["is_outlier"],
        "experiment_id",
    ]

    experiments = load_ssdi_experiments(
        oil_ids=ALL_OILS,
        nozzle_diameters=[2e-3, 3e-3],
        dispersion_kinds=["Untreated", "SSDI"],
    )

    experiments = experiments.loc[experiments["experiment_id"].isin(valid_ids)].copy()

    experiments = add_ssdi_physics(experiments)

    calibration = calibrate_ssdi(experiments)

    predictions = predict_ssdi(
        experiments=experiments,
        we=calibration.we,
        ca=calibration.ca,
        a=calibration.a_optimized,
        b=calibration.b_optimized,
        model_version=FILTERED_VERSION,
    )

    save_ssdi_results(predictions)

    return SSDIModelResult(
        model_version=FILTERED_VERSION,
        experiment_count=len(experiments),
        a_initial=calibration.a_initial,
        b_initial=calibration.b_initial,
        a_optimized=calibration.a_optimized,
        b_optimized=calibration.b_optimized,
        loss=calibration.loss,
    )
