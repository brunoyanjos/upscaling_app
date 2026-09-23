from upscaling_app.analysis.ssdi.io.data import load_ssdi_results
from upscaling_app.analysis.ssdi.metrics import (
    add_point_metrics,
    calculate_global_metrics,
)
from upscaling_app.analysis.ssdi.evaluation.oil_analysis import (
    add_oil_metadata,
    calculate_oil_metrics,
)
from upscaling_app.analysis.ssdi.outliers import mark_iqr_outliers
from upscaling_app.analysis.ssdi.io.persistence import (
    save_oil_metrics,
    save_ssdi_analysis,
)
from upscaling_app.analysis.ssdi.plotting import save_parity_plot


def run_ssdi_analysis(
    model_version: str,
):
    results = load_ssdi_results(model_version)

    results = add_point_metrics(results)
    results = mark_iqr_outliers(results)
    results = add_oil_metadata(results)

    metrics = calculate_global_metrics(results)

    oil_metrics = calculate_oil_metrics(results)

    save_oil_metrics(
        oil_metrics,
        model_version,
    )

    save_ssdi_analysis(
        results,
        model_version,
    )

    save_parity_plot(
        results=results,
        metrics=metrics,
        model_version=model_version,
    )

    return results, metrics
