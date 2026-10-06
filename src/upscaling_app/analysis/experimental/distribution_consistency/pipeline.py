from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.experimental.data import (
    load_distributions,
    load_experiments,
)
from upscaling_app.analysis.experimental.distribution_consistency.analysis import (
    analyze_distribution_consistency,
)
from upscaling_app.analysis.experimental.distribution_consistency.plotting import (
    save_d50_consistency_plot,
    save_reported_percentile_plot,
)
from upscaling_app.analysis.experimental.distribution_consistency.reporting import (
    print_distribution_consistency_report,
)


@dataclass(frozen=True)
class DistributionConsistencyResult:
    distributions: pd.DataFrame
    experiments: pd.DataFrame
    summary: pd.DataFrame
    comparison: pd.DataFrame


def run_distribution_consistency_analysis() -> DistributionConsistencyResult:
    distributions = load_distributions()
    experiments = load_experiments()

    summary, comparison = analyze_distribution_consistency(
        distributions=distributions,
        experiments=experiments,
    )

    return DistributionConsistencyResult(
        distributions=distributions,
        experiments=experiments,
        summary=summary,
        comparison=comparison,
    )


def run_distribution_consistency_workflow() -> DistributionConsistencyResult:
    result = run_distribution_consistency_analysis()

    output_dir = paths.RESULTS_DIR / "experimental" / "distribution_consistency"

    print_distribution_consistency_report(
        comparison=result.comparison,
    )

    save_d50_consistency_plot(
        comparison=result.comparison,
        output=(output_dir / "d50_consistency.png"),
    )

    save_reported_percentile_plot(
        comparison=result.comparison,
        output=(output_dir / "reported_d50_percentile.png"),
    )

    return result
