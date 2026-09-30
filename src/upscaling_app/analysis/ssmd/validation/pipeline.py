from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.ssmd.io.data import (
    load_model_predictions,
)
from upscaling_app.analysis.ssmd.validation.analysis import (
    build_leave_one_oil_out_predictions,
    build_validation_comparison,
    summarize_leave_one_oil_out,
    summarize_leave_one_oil_out_by_oil,
)
from upscaling_app.upscaling.ssdi.versions import (
    BASELINE_VERSION as DEFAULT_SSDI_SOURCE_VERSION,
)
from upscaling_app.upscaling.ssmd.io.data import (
    load_ssmd_calibration_dataset,
)
from upscaling_app.upscaling.ssmd.physics.derived_properties import (
    add_derived_properties,
)
from upscaling_app.upscaling.ssmd.versions import (
    GLOBAL_CD_VERSION,
)


@dataclass
class SSMDValidationResult:
    ssdi_source_version: str
    predictions: pd.DataFrame
    by_oil: pd.DataFrame
    summary: pd.DataFrame
    comparison: pd.DataFrame


def _prepare_validation_dataset() -> pd.DataFrame:
    dataset = load_ssmd_calibration_dataset()

    return add_derived_properties(
        dataset,
    )


def run_ssmd_validation_analysis(
    *,
    ssdi_source_version: str = DEFAULT_SSDI_SOURCE_VERSION,
) -> SSMDValidationResult:
    dataset = _prepare_validation_dataset()

    predictions = build_leave_one_oil_out_predictions(
        dataset,
    )

    by_oil = summarize_leave_one_oil_out_by_oil(
        predictions,
    )

    summary = summarize_leave_one_oil_out(
        predictions,
    )

    global_predictions = load_model_predictions(
        ssmd_model_version=GLOBAL_CD_VERSION,
        ssdi_source_version=ssdi_source_version,
    )

    comparison = build_validation_comparison(
        global_predictions,
        predictions,
    )

    return SSMDValidationResult(
        ssdi_source_version=ssdi_source_version,
        predictions=predictions,
        by_oil=by_oil,
        summary=summary,
        comparison=comparison,
    )


def run_ssmd_validation_workflow(
    *,
    ssdi_source_version: str = DEFAULT_SSDI_SOURCE_VERSION,
) -> SSMDValidationResult:
    from upscaling_app.analysis.ssmd.validation.persistence import (
        save_validation_results,
    )
    from upscaling_app.analysis.ssmd.validation.plotting import (
        save_loo_parity_plot,
        save_loo_residual_by_oil_plot,
    )
    from upscaling_app.analysis.ssmd.validation.reporting import (
        print_validation_report,
    )

    result = run_ssmd_validation_analysis(
        ssdi_source_version=ssdi_source_version,
    )

    save_validation_results(
        result,
    )

    print_validation_report(
        result,
    )

    save_loo_parity_plot(
        predictions=result.predictions,
        output=(paths.SSMD_VALIDATION_FIGURES_DIR / "loo_parity.png"),
    )

    save_loo_residual_by_oil_plot(
        by_oil=result.by_oil,
        output=(paths.SSMD_VALIDATION_FIGURES_DIR / "loo_residual_by_oil.png"),
    )

    return result
