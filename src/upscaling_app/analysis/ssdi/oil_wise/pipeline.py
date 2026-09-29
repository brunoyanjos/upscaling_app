from upscaling_app import paths
from upscaling_app.analysis.ssdi.oil_wise.analysis import (
    OilWiseComparisonResult,
    run_oil_wise_comparison_analysis,
)
from upscaling_app.analysis.ssdi.oil_wise.persistence import (
    save_oil_wise_comparison,
)
from upscaling_app.analysis.ssdi.oil_wise.plotting import (
    save_oil_wise_log_mse_plot,
)
from upscaling_app.analysis.ssdi.oil_wise.reporting import (
    print_oil_wise_comparison_report,
)
from upscaling_app.analysis.ssdi.performance.plotting import (
    save_performance_parity_plot,
)


def run_oil_wise_comparison_workflow() -> OilWiseComparisonResult:
    result = run_oil_wise_comparison_analysis()

    save_oil_wise_comparison(
        overall=result.overall,
        by_oil=result.by_oil,
    )

    oil_wise_metrics = result.overall.set_index("model").loc["oil_wise"].to_dict()

    save_performance_parity_plot(
        results=result.oil_wise_results,
        metrics=oil_wise_metrics,
        output=(paths.SSDI_OIL_WISE_FIGURES_DIR / "oil_wise_parity.png"),
    )

    save_oil_wise_log_mse_plot(
        by_oil=result.by_oil,
        output=(paths.SSDI_OIL_WISE_FIGURES_DIR / "log_mse_by_oil.png"),
    )

    print_oil_wise_comparison_report(result)

    return result
