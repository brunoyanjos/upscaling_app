from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.ssmd.io.data import (
    load_model_calibrations,
    load_model_predictions,
)
from upscaling_app.analysis.ssmd.oil_wise.analysis import (
    build_oil_wise_comparison,
    summarize_oil_wise_comparison,
)
from upscaling_app.upscaling.ssdi.versions import (
    BASELINE_VERSION as DEFAULT_SSDI_SOURCE_VERSION,
)
from upscaling_app.upscaling.ssmd.versions import (
    GLOBAL_CD_VERSION,
    OIL_WISE_FACTOR_VERSION,
)


@dataclass
class SSMDOilWiseResult:
    ssdi_source_version: str
    comparison: pd.DataFrame
    summary: pd.DataFrame


def run_ssmd_oil_wise_analysis(
    *,
    ssdi_source_version: str = DEFAULT_SSDI_SOURCE_VERSION,
) -> SSMDOilWiseResult:
    global_predictions = load_model_predictions(
        ssmd_model_version=GLOBAL_CD_VERSION,
        ssdi_source_version=ssdi_source_version,
    )

    oil_wise_calibrations = load_model_calibrations(
        ssmd_model_version=OIL_WISE_FACTOR_VERSION,
    )

    comparison = build_oil_wise_comparison(
        global_predictions,
        oil_wise_calibrations,
    )

    summary = summarize_oil_wise_comparison(
        comparison,
    )

    return SSMDOilWiseResult(
        ssdi_source_version=ssdi_source_version,
        comparison=comparison,
        summary=summary,
    )


def run_ssmd_oil_wise_workflow(
    *,
    ssdi_source_version: str = DEFAULT_SSDI_SOURCE_VERSION,
) -> SSMDOilWiseResult:
    from upscaling_app.analysis.ssmd.oil_wise.persistence import (
        save_oil_wise_results,
    )
    from upscaling_app.analysis.ssmd.oil_wise.plotting import (
        save_factor_comparison_plot,
        save_factor_variability_plot,
    )
    from upscaling_app.analysis.ssmd.oil_wise.reporting import (
        print_oil_wise_analysis_report,
    )

    result = run_ssmd_oil_wise_analysis(
        ssdi_source_version=ssdi_source_version,
    )

    save_oil_wise_results(
        result,
    )

    print_oil_wise_analysis_report(
        result,
    )

    save_factor_comparison_plot(
        comparison=result.comparison,
        output=(paths.SSMD_OIL_WISE_FIGURES_DIR / "k_global_vs_oil_wise.png"),
    )

    save_factor_variability_plot(
        comparison=result.comparison,
        output=(paths.SSMD_OIL_WISE_FIGURES_DIR / "k_oil_variability.png"),
    )

    return result
