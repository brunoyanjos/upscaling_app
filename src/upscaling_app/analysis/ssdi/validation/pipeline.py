from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.ssdi.performance.plotting import (
    save_performance_parity_plot,
)
from upscaling_app.analysis.ssdi.populations import (
    SSDI_ALL_OILS,
    SSDI_EXTENDED_SENSITIVITY_OILS,
    SSDI_RETAINED_OILS,
)
from upscaling_app.analysis.ssdi.validation.analysis import (
    run_excluded_oil_challenge,
    run_leave_one_oil_out_analysis,
)
from upscaling_app.analysis.ssdi.validation.persistence import (
    save_excluded_challenge_result,
    save_loo_result,
)
from upscaling_app.analysis.ssdi.validation.plotting import (
    save_loo_bias_plot,
    save_loo_log_mse_plot,
    save_loo_mape_plot,
)
from upscaling_app.analysis.ssdi.validation.reporting import (
    print_excluded_challenge_report,
    print_loo_report,
)


@dataclass(frozen=True)
class LeaveOneOilOutResult:
    name: str
    folds: pd.DataFrame
    predictions: pd.DataFrame
    global_metrics: dict[str, float]
    oil_metrics: pd.DataFrame


@dataclass(frozen=True)
class ExcludedChallengeResult:
    predictions: pd.DataFrame
    global_metrics: dict[str, float]
    oil_metrics: pd.DataFrame
    calibration: pd.DataFrame


def _run_loo(
    *,
    name: str,
    oil_ids: tuple[int, ...],
) -> LeaveOneOilOutResult:
    (
        folds,
        predictions,
        global_metrics,
        oil_metrics,
    ) = run_leave_one_oil_out_analysis(
        oil_ids=oil_ids,
        validation_name=name,
    )

    return LeaveOneOilOutResult(
        name=name,
        folds=folds,
        predictions=predictions,
        global_metrics=global_metrics,
        oil_metrics=oil_metrics,
    )


def _save_loo_outputs(
    result: LeaveOneOilOutResult,
) -> None:
    save_loo_result(
        name=result.name,
        folds=result.folds,
        predictions=result.predictions,
        global_metrics=result.global_metrics,
        oil_metrics=result.oil_metrics,
    )

    save_performance_parity_plot(
        results=result.predictions,
        metrics=result.global_metrics,
        output=(paths.SSDI_VALIDATION_FIGURES_DIR / f"{result.name}_parity.png"),
    )

    save_loo_log_mse_plot(
        folds=result.folds,
        output=(
            paths.SSDI_VALIDATION_FIGURES_DIR / f"{result.name}_log_mse_by_oil.png"
        ),
    )

    save_loo_mape_plot(
        folds=result.folds,
        output=(paths.SSDI_VALIDATION_FIGURES_DIR / f"{result.name}_mape_by_oil.png"),
    )

    save_loo_bias_plot(
        folds=result.folds,
        output=(
            paths.SSDI_VALIDATION_FIGURES_DIR
            / f"{result.name}_mean_log_residual_by_oil.png"
        ),
    )


def run_loo_all_workflow() -> LeaveOneOilOutResult:
    result = _run_loo(
        name="loo_all",
        oil_ids=SSDI_ALL_OILS,
    )

    _save_loo_outputs(result)

    print_loo_report(
        title="SSDI LEAVE-ONE-OIL-OUT — ALL OILS",
        folds=result.folds,
        global_metrics=result.global_metrics,
    )

    return result


def run_loo_retained_workflow() -> LeaveOneOilOutResult:
    result = _run_loo(
        name="loo_retained",
        oil_ids=SSDI_RETAINED_OILS,
    )

    _save_loo_outputs(result)

    print_loo_report(
        title="SSDI LEAVE-ONE-OIL-OUT — RETAINED OILS",
        folds=result.folds,
        global_metrics=result.global_metrics,
    )

    return result


def run_excluded_challenge_workflow() -> ExcludedChallengeResult:
    (
        predictions,
        global_metrics,
        oil_metrics,
        calibration,
    ) = run_excluded_oil_challenge(
        train_oils=SSDI_RETAINED_OILS,
        challenge_oils=SSDI_EXTENDED_SENSITIVITY_OILS,
    )

    result = ExcludedChallengeResult(
        predictions=predictions,
        global_metrics=global_metrics,
        oil_metrics=oil_metrics,
        calibration=calibration,
    )

    save_excluded_challenge_result(
        calibration=result.calibration,
        predictions=result.predictions,
        global_metrics=result.global_metrics,
        oil_metrics=result.oil_metrics,
    )

    save_performance_parity_plot(
        results=result.predictions,
        metrics=result.global_metrics,
        output=(paths.SSDI_VALIDATION_FIGURES_DIR / "excluded_challenge_parity.png"),
    )

    print_excluded_challenge_report(
        calibration=result.calibration,
        oil_metrics=result.oil_metrics,
        global_metrics=result.global_metrics,
    )

    return result


def run_validation_comparison_workflow() -> pd.DataFrame:
    from upscaling_app.analysis.ssdi.validation.analysis import (
        build_validation_comparison,
    )
    from upscaling_app.analysis.ssdi.validation.persistence import (
        load_validation_global,
        save_validation_comparison,
    )
    from upscaling_app.analysis.ssdi.validation.plotting import (
        save_validation_comparison_plot,
    )
    from upscaling_app.analysis.ssdi.validation.reporting import (
        print_validation_comparison_report,
    )

    loo_all = load_validation_global(
        "loo_all_global",
    )

    loo_retained = load_validation_global(
        "loo_retained_global",
    )

    excluded_challenge = load_validation_global(
        "excluded_challenge_global",
    )

    comparison = build_validation_comparison(
        loo_all=loo_all,
        loo_retained=loo_retained,
        excluded_challenge=excluded_challenge,
    )

    save_validation_comparison(comparison)

    save_validation_comparison_plot(
        comparison=comparison,
        output=(paths.SSDI_VALIDATION_FIGURES_DIR / "validation_comparison.png"),
    )

    print_validation_comparison_report(comparison)

    return comparison
