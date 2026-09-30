from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.ssmd.io.data import (
    load_model_predictions,
)
from upscaling_app.analysis.ssmd.performance.analysis import (
    build_performance_comparison,
)
from upscaling_app.upscaling.ssdi.versions import (
    BASELINE_VERSION as DEFAULT_SSDI_SOURCE_VERSION,
)
from upscaling_app.upscaling.ssmd.versions import (
    GLOBAL_CD_VERSION,
    SINTEF_REFERENCE_VERSION,
)


@dataclass
class SSMDPerformanceResult:
    ssdi_source_version: str
    reference: pd.DataFrame
    global_model: pd.DataFrame
    comparison: pd.DataFrame


def run_ssmd_performance_analysis(
    *,
    ssdi_source_version: str = DEFAULT_SSDI_SOURCE_VERSION,
) -> SSMDPerformanceResult:
    reference = load_model_predictions(
        ssmd_model_version=SINTEF_REFERENCE_VERSION,
        ssdi_source_version=ssdi_source_version,
    )

    global_model = load_model_predictions(
        ssmd_model_version=GLOBAL_CD_VERSION,
        ssdi_source_version=ssdi_source_version,
    )

    comparison = build_performance_comparison(
        reference,
        global_model,
    )

    return SSMDPerformanceResult(
        ssdi_source_version=ssdi_source_version,
        reference=reference,
        global_model=global_model,
        comparison=comparison,
    )


def run_ssmd_performance_workflow(
    *,
    ssdi_source_version: str = DEFAULT_SSDI_SOURCE_VERSION,
) -> SSMDPerformanceResult:
    from upscaling_app.analysis.ssmd.performance.persistence import (
        save_performance_results,
    )
    from upscaling_app.analysis.ssmd.performance.plotting import (
        save_d50_parity_plot,
        save_dR_parity_plot,
    )
    from upscaling_app.analysis.ssmd.performance.reporting import (
        print_performance_report,
    )

    result = run_ssmd_performance_analysis(
        ssdi_source_version=ssdi_source_version,
    )

    save_performance_results(
        result.comparison,
    )

    print_performance_report(
        result,
    )

    save_dR_parity_plot(
        reference=result.reference,
        global_model=result.global_model,
        output=(paths.SSMD_PERFORMANCE_FIGURES_DIR / "dR_parity_comparison.png"),
    )

    save_d50_parity_plot(
        reference=result.reference,
        global_model=result.global_model,
        output=(paths.SSMD_PERFORMANCE_FIGURES_DIR / "d50_parity_comparison.png"),
    )

    return result
