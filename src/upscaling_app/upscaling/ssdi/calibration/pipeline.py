from dataclasses import dataclass

import pandas as pd

from upscaling_app.upscaling.ssdi.calibration.initial_guess import (
    estimate_initial_coefficients,
)
from upscaling_app.upscaling.ssdi.calibration.optimization import (
    optimize_coefficients,
    optimize_coefficients_oil_wise,
)
from upscaling_app.upscaling.ssdi.calibration.preparation import (
    prepare_calibration_arrays,
)


@dataclass(frozen=True)
class CalibrationResult:
    we: object
    ca: object
    d50_d: object
    a_initial: float
    b_initial: float
    a_optimized: float
    b_optimized: float
    loss: float


def calibrate_ssdi(
    experiments: pd.DataFrame,
    b_grid: tuple[float, float] = (0.01, 1.0),
    b_bounds: tuple[float | None, float | None] = (1e-3, None),
) -> CalibrationResult:
    we, ca, d50_d = prepare_calibration_arrays(experiments)

    a_initial, b_initial = estimate_initial_coefficients(
        we,
        ca,
        d50_d,
        b_min=b_grid[0],
        b_max=b_grid[1],
    )

    a_optimized, b_optimized, loss = optimize_coefficients(
        we,
        ca,
        d50_d,
        a_initial,
        b_initial,
        b_bounds=b_bounds,
    )

    return CalibrationResult(
        we=we,
        ca=ca,
        d50_d=d50_d,
        a_initial=a_initial,
        b_initial=b_initial,
        a_optimized=a_optimized,
        b_optimized=b_optimized,
        loss=loss,
    )


def calibrate_ssdi_oil_wise(
    experiments: pd.DataFrame,
) -> CalibrationResult:
    we, ca, d50_d = prepare_calibration_arrays(
        experiments,
    )

    a_initial, b_initial = estimate_initial_coefficients(
        we,
        ca,
        d50_d,
        b_min=-0.5,
        b_max=1.0,
        solver="newton",
    )

    a_optimized, b_optimized, loss = optimize_coefficients_oil_wise(
        we,
        ca,
        d50_d,
        a_initial,
        b_initial,
    )

    return CalibrationResult(
        we=we,
        ca=ca,
        d50_d=d50_d,
        a_initial=a_initial,
        b_initial=b_initial,
        a_optimized=a_optimized,
        b_optimized=b_optimized,
        loss=loss,
    )
