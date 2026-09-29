import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.ssdi.comparison.analysis import (
    build_ssdi_model_comparison,
)
from upscaling_app.analysis.ssdi.comparison.persistence import (
    save_model_comparison,
)
from upscaling_app.analysis.ssdi.comparison.plotting import (
    save_model_comparison_plot,
)
from upscaling_app.analysis.ssdi.comparison.reporting import (
    print_model_comparison_report,
)


def run_ssdi_model_comparison_analysis() -> pd.DataFrame:
    return build_ssdi_model_comparison()


def run_ssdi_model_comparison_workflow() -> pd.DataFrame:
    comparison = run_ssdi_model_comparison_analysis()

    save_model_comparison(
        comparison,
    )

    save_model_comparison_plot(
        comparison=comparison,
        output=(paths.SSDI_COMPARISON_FIGURES_DIR / "log_mse_comparison.png"),
    )

    print_model_comparison_report(
        comparison,
    )

    return comparison
