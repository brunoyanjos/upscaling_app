import jax.numpy as jnp
import pandas as pd

from upscaling_app.upscaling.ssdi.calibration.optimization import loss_fn
from upscaling_app.upscaling.ssdi.calibration.pipeline import calibrate_ssdi
from upscaling_app.upscaling.ssdi.io.data import load_ssdi_experiments
from upscaling_app.upscaling.ssdi.io.persistence import save_ssdi_results
from upscaling_app.upscaling.ssdi.physics.derived_properties import add_ssdi_physics
from upscaling_app.upscaling.ssdi.prediction import predict_ssdi
from upscaling_app.upscaling.ssdi.results import BaselineResult, SSDIModelResult
from upscaling_app.upscaling.ssdi.versions import (
    BASELINE_VERSION,
    REFERENCE_VERSION,
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

A_REFERENCE = 24.6
B_REFERENCE = 0.08


def run_baseline() -> BaselineResult:
    experiments = load_ssdi_experiments(
        oil_ids=ALL_OILS,
        nozzle_diameters=[2e-3, 3e-3],
        dispersion_kinds=["Untreated", "SSDI"],
    )

    experiments = add_ssdi_physics(experiments)

    calibration = calibrate_ssdi(experiments)

    reference_params = jnp.array([A_REFERENCE, B_REFERENCE])

    loss_reference = float(
        loss_fn(
            reference_params,
            calibration.we,
            calibration.ca,
            calibration.d50_d,
        )
    )

    optimized_predictions = predict_ssdi(
        experiments=experiments,
        we=calibration.we,
        ca=calibration.ca,
        a=calibration.a_optimized,
        b=calibration.b_optimized,
        model_version=BASELINE_VERSION,
    )

    reference_predictions = predict_ssdi(
        experiments=experiments,
        we=calibration.we,
        ca=calibration.ca,
        a=A_REFERENCE,
        b=B_REFERENCE,
        model_version=REFERENCE_VERSION,
    )

    results = pd.concat(
        [
            optimized_predictions,
            reference_predictions,
        ],
        ignore_index=True,
    )

    save_ssdi_results(results)

    return BaselineResult(
        model=SSDIModelResult(
            model_version=BASELINE_VERSION,
            experiment_count=len(experiments),
            a_initial=calibration.a_initial,
            b_initial=calibration.b_initial,
            a_optimized=calibration.a_optimized,
            b_optimized=calibration.b_optimized,
            loss=calibration.loss,
        ),
        a_reference=A_REFERENCE,
        b_reference=B_REFERENCE,
        loss_reference=loss_reference,
    )
