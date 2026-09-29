from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.ssdi.io.data import (
    load_ssdi_results,
)
from upscaling_app.analysis.ssdi.metrics import (
    add_point_metrics,
    calculate_global_metrics,
)
from upscaling_app.analysis.ssdi.sensitivity.analysis import (
    EXTENDED_SENSITIVITY_OILS,
    RESIDUAL_SENSITIVITY_OILS,
    select_iqr_population,
    select_oil_exclusion_population,
)
from upscaling_app.analysis.ssdi.sensitivity.persistence import (
    save_sensitivity_result,
)
from upscaling_app.analysis.ssdi.sensitivity.plotting import (
    save_sensitivity_parity_plot,
)
from upscaling_app.analysis.ssdi.sensitivity.reporting import (
    print_sensitivity_report,
)
from upscaling_app.upscaling.ssdi.calibration.pipeline import (
    calibrate_ssdi,
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
    BASELINE_VERSION,
    FILTERED_VERSION,
    OIL_EXTENDED_SENSITIVITY_VERSION,
    OIL_RESIDUAL_SENSITIVITY_VERSION,
)


@dataclass(frozen=True)
class SensitivityResult:
    name: str
    model_version: str

    experiment_count: int
    excluded_count: int

    a_initial: float
    b_initial: float

    a_optimized: float
    b_optimized: float

    log_mse: float

    predictions: pd.DataFrame
    plot_data: pd.DataFrame
    excluded: pd.DataFrame
    metrics: dict[str, float]


def _load_experiments() -> pd.DataFrame:
    return load_ssdi_experiments(
        oil_ids=SSDI_OIL_IDS,
        nozzle_diameters=SSDI_NOZZLE_DIAMETERS,
        dispersion_kinds=SSDI_DISPERSION_KINDS,
    )


def _build_calibration_table(
    result: SensitivityResult,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "model_version": result.model_version,
                "calibration_scope": (f"sensitivity_{result.name}"),
                "oil_id": pd.NA,
                "experiment_count": (result.experiment_count),
                "solver": "fixed_point",
                "optimizer": "L-BFGS-B",
                "a_initial": result.a_initial,
                "b_initial": result.b_initial,
                "a_optimized": result.a_optimized,
                "b_optimized": result.b_optimized,
                "log_mse": result.log_mse,
            }
        ]
    )


def _build_summary(
    result: SensitivityResult,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "model_version": result.model_version,
                "experiment_count": (result.experiment_count),
                "excluded_count": (result.excluded_count),
                "a_optimized": result.a_optimized,
                "b_optimized": result.b_optimized,
                "log_mse": result.metrics["log_mse"],
                "r2": result.metrics["r2"],
                "rmse": result.metrics["rmse"],
                "mape": result.metrics["mape"],
            }
        ]
    )


def _calibrate_population(
    *,
    name: str,
    model_version: str,
    experiments: pd.DataFrame,
    excluded: pd.DataFrame,
) -> SensitivityResult:
    experiments = add_ssdi_physics(
        experiments,
    )

    calibration = calibrate_ssdi(
        experiments,
    )

    predictions = predict_ssdi(
        experiments=experiments,
        we=calibration.we,
        ca=calibration.ca,
        a=calibration.a_optimized,
        b=calibration.b_optimized,
        model_version=model_version,
    )

    plot_data = predictions.merge(
        experiments[
            [
                "experiment_id",
                "dispersion_tag",
                "nozzle_diameter",
            ]
        ],
        on="experiment_id",
        how="left",
        validate="one_to_one",
    )

    analyzed = add_point_metrics(
        predictions,
    )

    metrics = calculate_global_metrics(
        analyzed,
    )

    result = SensitivityResult(
        name=name,
        model_version=model_version,
        experiment_count=len(experiments),
        excluded_count=len(excluded),
        a_initial=calibration.a_initial,
        b_initial=calibration.b_initial,
        a_optimized=calibration.a_optimized,
        b_optimized=calibration.b_optimized,
        log_mse=calibration.loss,
        predictions=predictions,
        plot_data=plot_data,
        excluded=excluded,
        metrics=metrics,
    )

    save_ssdi_results(
        predictions,
    )

    save_ssdi_calibrations(
        _build_calibration_table(result),
    )

    save_sensitivity_result(
        name=name,
        summary=_build_summary(result),
        excluded=excluded,
    )

    return result


def run_iqr_sensitivity() -> SensitivityResult:
    experiments = _load_experiments()

    baseline_predictions = load_ssdi_results(
        BASELINE_VERSION,
    )

    selected, excluded = select_iqr_population(
        experiments=experiments,
        baseline_predictions=baseline_predictions,
    )

    return _calibrate_population(
        name="iqr",
        model_version=FILTERED_VERSION,
        experiments=selected,
        excluded=excluded,
    )


def run_oil_residual_sensitivity() -> SensitivityResult:
    experiments = _load_experiments()

    selected, excluded = select_oil_exclusion_population(
        experiments=experiments,
        oil_ids=RESIDUAL_SENSITIVITY_OILS,
    )

    return _calibrate_population(
        name="oil_residual",
        model_version=(OIL_RESIDUAL_SENSITIVITY_VERSION),
        experiments=selected,
        excluded=excluded,
    )


def run_oil_extended_sensitivity() -> SensitivityResult:
    experiments = _load_experiments()

    selected, excluded = select_oil_exclusion_population(
        experiments=experiments,
        oil_ids=EXTENDED_SENSITIVITY_OILS,
    )

    return _calibrate_population(
        name="oil_extended",
        model_version=(OIL_EXTENDED_SENSITIVITY_VERSION),
        experiments=selected,
        excluded=excluded,
    )


def _run_sensitivity_workflow(
    result: SensitivityResult,
    *,
    title: str,
    figure_name: str,
    excluded_oils: tuple[int, ...] | None = None,
) -> SensitivityResult:
    save_sensitivity_parity_plot(
        results=result.plot_data,
        metrics=result.metrics,
        output=(paths.SSDI_SENSITIVITY_FIGURES_DIR / figure_name),
    )

    print_sensitivity_report(
        title=title,
        experiment_count=result.experiment_count,
        excluded_count=result.excluded_count,
        excluded_oils=excluded_oils,
        a_initial=result.a_initial,
        b_initial=result.b_initial,
        a_optimized=result.a_optimized,
        b_optimized=result.b_optimized,
        metrics=result.metrics,
    )

    return result


def run_iqr_sensitivity_workflow() -> SensitivityResult:
    return _run_sensitivity_workflow(
        run_iqr_sensitivity(),
        title="SSDI IQR SENSITIVITY",
        figure_name="iqr_parity.png",
    )


def run_oil_residual_sensitivity_workflow() -> SensitivityResult:
    return _run_sensitivity_workflow(
        run_oil_residual_sensitivity(),
        title="SSDI OIL-RESIDUAL SENSITIVITY",
        figure_name="oil_residual_parity.png",
        excluded_oils=RESIDUAL_SENSITIVITY_OILS,
    )


def run_oil_extended_sensitivity_workflow() -> SensitivityResult:
    return _run_sensitivity_workflow(
        run_oil_extended_sensitivity(),
        title="SSDI EXTENDED OIL SENSITIVITY",
        figure_name="oil_extended_parity.png",
        excluded_oils=EXTENDED_SENSITIVITY_OILS,
    )
