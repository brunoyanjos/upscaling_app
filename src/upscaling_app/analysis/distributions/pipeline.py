from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths

from upscaling_app.analysis.distributions.data import (
    load_distributions,
    load_experiments,
)
from upscaling_app.analysis.distributions.descriptive import (
    summarize_distributions,
)
from upscaling_app.analysis.distributions.validation import (
    compare_distribution_d50,
)
from upscaling_app.analysis.distributions.plotting import (
    plot_suspicious_distributions,
)


@dataclass(frozen=True)
class DistributionAnalysisResult:
    data: pd.DataFrame
    summary: pd.DataFrame
    d50_comparison: pd.DataFrame


def run_distribution_analysis() -> DistributionAnalysisResult:
    distributions = load_distributions()
    experiments = load_experiments()

    summary = summarize_distributions(distributions)

    d50_comparison = compare_distribution_d50(
        summary,
        experiments,
    )

    plot_suspicious_distributions(
        distributions=distributions,
        comparison=d50_comparison,
        output_dir=paths.RESULTS_DIR / "distributions" / "d50_checks",
    )

    return DistributionAnalysisResult(
        data=distributions,
        summary=summary,
        d50_comparison=d50_comparison,
    )
