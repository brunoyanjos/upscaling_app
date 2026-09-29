from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.ssdi.io.data import (
    load_ssdi_results,
)
from upscaling_app.analysis.ssdi.metrics import (
    calculate_global_metrics,
)
from upscaling_app.analysis.ssdi.performance.analysis import (
    calculate_oil_metrics,
    prepare_performance_results,
)
from upscaling_app.analysis.ssdi.performance.persistence import (
    save_performance_result,
)
from upscaling_app.analysis.ssdi.performance.plotting import (
    save_performance_parity_plot,
)
from upscaling_app.analysis.ssdi.performance.reporting import (
    print_performance_report,
)


@dataclass(frozen=True)
class SSDIPerformanceResult:
    model_version: str
    model_label: str

    results: pd.DataFrame
    global_metrics: dict[str, float]
    oil_metrics: pd.DataFrame


def run_ssdi_performance_analysis(
    *,
    model_version: str,
    model_label: str,
) -> SSDIPerformanceResult:
    predictions = load_ssdi_results(
        model_version,
    )

    results = prepare_performance_results(
        predictions,
    )

    global_metrics = calculate_global_metrics(
        results,
    )

    oil_metrics = calculate_oil_metrics(
        results,
    )

    return SSDIPerformanceResult(
        model_version=model_version,
        model_label=model_label,
        results=results,
        global_metrics=global_metrics,
        oil_metrics=oil_metrics,
    )


def run_ssdi_performance_workflow(
    *,
    model_version: str,
    model_label: str,
    figure_name: str,
) -> SSDIPerformanceResult:
    result = run_ssdi_performance_analysis(
        model_version=model_version,
        model_label=model_label,
    )

    save_performance_result(
        model_version=result.model_version,
        results=result.results,
        global_metrics=result.global_metrics,
        oil_metrics=result.oil_metrics,
    )

    save_performance_parity_plot(
        results=result.results,
        metrics=result.global_metrics,
        output=(paths.SSDI_PERFORMANCE_FIGURES_DIR / figure_name),
    )

    print_performance_report(
        result,
    )

    return result
