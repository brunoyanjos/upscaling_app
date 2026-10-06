from dataclasses import dataclass

from upscaling_app import paths
import pandas as pd

from upscaling_app.analysis.distributions.analysis import (
    compare_distribution_fit_methods,
    evaluate_distribution_fits,
    summarize_distribution_fit_metrics,
    summarize_fit_method_comparison_by_regime,
    test_distribution_fit_improvement,
)
from upscaling_app.analysis.experimental.data import (
    load_distributions,
    load_experiments,
)

from upscaling_app.analysis.distributions.persistence import (
    save_distribution_fit_evaluation,
    save_distribution_method_comparison,
)
from upscaling_app.analysis.distributions.plotting import (
    save_method_improvement_by_regime_plot,
    save_method_win_fraction_plot,
)

EXPERIMENT_METADATA_COLUMNS = [
    "experiment_id",
    "oil_id",
    "dispersion_kind",
    "dispersion_tag",
    "nozzle_diameter",
    "has_gas",
    "measured_d50",
]


@dataclass(frozen=True)
class DistributionFitAnalysisResult:
    parameters: pd.DataFrame
    evaluation: pd.DataFrame
    summary: pd.DataFrame
    comparison: pd.DataFrame
    comparison_summary: pd.DataFrame
    comparison_by_regime: pd.DataFrame
    statistical_comparison: pd.DataFrame


def _select_experiment_metadata(
    experiments: pd.DataFrame,
) -> pd.DataFrame:
    missing = [
        column
        for column in EXPERIMENT_METADATA_COLUMNS
        if column not in experiments.columns
    ]

    if missing:
        raise ValueError("Missing experiment metadata columns: " + ", ".join(missing))

    metadata = experiments[EXPERIMENT_METADATA_COLUMNS].copy()

    if metadata["experiment_id"].duplicated().any():
        raise ValueError("experiments contains duplicated experiment_id values.")

    return metadata


def run_distribution_fit_analysis(
    parameters: pd.DataFrame,
) -> DistributionFitAnalysisResult:
    distributions = load_distributions()
    experiments = load_experiments()

    evaluation = evaluate_distribution_fits(
        distributions=distributions,
        parameters=parameters,
    )

    metadata = _select_experiment_metadata(experiments)

    evaluation = metadata.merge(
        evaluation,
        on="experiment_id",
        how="inner",
        validate="one_to_one",
    )

    if len(evaluation) != len(parameters):
        raise ValueError(
            "Not all fitted distributions could be matched to experiment metadata."
        )

    evaluation = evaluation.sort_values(
        [
            "dispersion_kind",
            "oil_id",
            "experiment_id",
        ]
    ).reset_index(drop=True)

    summary = summarize_distribution_fit_metrics(evaluation)

    (
        comparison,
        comparison_summary,
    ) = compare_distribution_fit_methods(evaluation)

    comparison_by_regime = summarize_fit_method_comparison_by_regime(comparison)

    statistical_comparison = test_distribution_fit_improvement(comparison)

    return DistributionFitAnalysisResult(
        parameters=parameters.copy(),
        evaluation=evaluation,
        summary=summary,
        comparison=comparison,
        comparison_summary=comparison_summary,
        comparison_by_regime=comparison_by_regime,
        statistical_comparison=statistical_comparison,
    )


def run_distribution_fit_workflow(
    parameters: pd.DataFrame,
) -> DistributionFitAnalysisResult:
    result = run_distribution_fit_analysis(parameters=parameters)

    save_distribution_fit_evaluation(result.evaluation)

    save_distribution_method_comparison(
        global_summary=result.summary,
        paired_comparison=result.comparison,
        by_regime=result.comparison_by_regime,
        statistical_tests=result.statistical_comparison,
    )

    save_method_win_fraction_plot(
        comparison_summary=(result.comparison_summary),
        output=(paths.DISTRIBUTION_ANALYSIS_FIGURES_DIR / "method_win_fraction.png"),
    )

    save_method_improvement_by_regime_plot(
        comparison_by_regime=(result.comparison_by_regime),
        output=(
            paths.DISTRIBUTION_ANALYSIS_FIGURES_DIR / "method_improvement_by_regime.png"
        ),
    )

    return result
