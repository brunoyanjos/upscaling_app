from __future__ import annotations

from dataclasses import dataclass

from upscaling_app.analysis.ssmd.oil_wise import (
    SSMDLocalComparison,
    build_oil_wise_comparison,
)
from upscaling_app.analysis.ssmd.performance import (
    SSMDPerformanceComparison,
    build_ssmd_performance_comparison,
)
from upscaling_app.analysis.ssmd.plotting import (
    save_ssmd_model_parity_comparison,
    save_ssmd_regime_performance_plot,
)
from upscaling_app.analysis.ssmd.reporting import (
    print_oil_wise_comparison,
    print_performance_comparison,
)


@dataclass(frozen=True)
class SSMDLocalAnalysisResult:
    oil_wise: SSMDLocalComparison
    performance: SSMDPerformanceComparison


def run_ssmd_oil_wise_analysis() -> SSMDLocalAnalysisResult:
    oil_wise = build_oil_wise_comparison()
    performance = build_ssmd_performance_comparison()

    print_oil_wise_comparison(oil_wise)
    print_performance_comparison(performance)

    save_ssmd_model_parity_comparison(
        performance.predictions,
        performance.overall,
    )
    save_ssmd_regime_performance_plot(
        performance.by_regime,
    )

    return SSMDLocalAnalysisResult(
        oil_wise=oil_wise,
        performance=performance,
    )
