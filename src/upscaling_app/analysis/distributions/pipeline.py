from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.distributions.analysis import (
    add_d50_diagnostics,
    build_cdf_validation_points,
    build_distribution_fit_curves,
    evaluate_distribution_fits,
    select_representative_fit_cases,
    summarize_d50_diagnostics,
    summarize_distribution_fit_metrics,
    summarize_distribution_fit_metrics_by_regime,
)
from upscaling_app.analysis.distributions.persistence import (
    save_distribution_fit_analysis,
)
from upscaling_app.analysis.distributions.plotting import (
    save_cdf_fit,
    save_d50_parity_plot,
    save_d50_relative_error_plot,
    save_d50_source_parity_plot,
    save_pdf_fit,
)
from upscaling_app.analysis.distributions.reporting import (
    report_distribution_analysis,
)
from upscaling_app.analysis.experimental.data import (
    load_distributions,
    load_experiments,
)
from upscaling_app.plotting.colors import get_base_color
from upscaling_app.upscaling.distributions.persistence import (
    load_distribution_parameters,
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
    cdf_points: pd.DataFrame
    fit_summary: pd.DataFrame
    fit_summary_by_regime: pd.DataFrame
    d50_summary: pd.DataFrame


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


def _experimental_color(
    dispersion_kind: str,
    dispersion_tag: str,
) -> str:
    if dispersion_kind == "Untreated":
        return get_base_color("untreated")

    if dispersion_kind == "SSDI":
        if "C9500" in dispersion_tag:
            return get_base_color("ssdi_corexit")

        return get_base_color("ssdi_finasol")

    return get_base_color("ssmd")


def _save_representative_fit_plots(
    *,
    selected_cases: pd.DataFrame,
    distributions: pd.DataFrame,
    parameters: pd.DataFrame,
) -> None:
    parameter_table = parameters.set_index("experiment_id")

    representative_dir = (
        paths.DISTRIBUTION_ANALYSIS_FIGURES_DIR / "representative_cases"
    )

    cdf_dir = representative_dir / "cdf"
    pdf_dir = representative_dir / "pdf"

    for case in selected_cases.itertuples(index=False):
        experiment_id = case.experiment_id

        distribution = distributions.loc[
            distributions["experiment_id"] == experiment_id
        ].copy()

        fitted = parameter_table.loc[experiment_id]

        curves = build_distribution_fit_curves(
            distribution=distribution,
            fitted=fitted,
        )

        experimental_color = _experimental_color(
            dispersion_kind=case.dispersion_kind,
            dispersion_tag=case.dispersion_tag,
        )

        prefix = (
            f"{case.case_group}_"
            f"{int(case.case_rank):02d}_"
            f"oil_{int(case.oil_id)}"
        )

        save_cdf_fit(
            diameter=curves["diameter"],
            experimental_cdf=curves["experimental_cdf"],
            fitted_cdf_at_data=curves["fitted_cdf_at_data"],
            rr_diameter=curves["rr_diameter"],
            fitted_cdf=curves["fitted_cdf"],
            output=(cdf_dir / f"{prefix}.png"),
            experimental_color=experimental_color,
            plot_max_diameter=float(curves["plot_max_diameter"]),
        )

        save_pdf_fit(
            edges=curves["pdf_edges"],
            experimental_density=curves["experimental_pdf"],
            rr_diameter=curves["rr_diameter"],
            fitted_density=curves["fitted_pdf"],
            output=(pdf_dir / f"{prefix}.png"),
            experimental_color=experimental_color,
            plot_max_diameter=float(curves["plot_max_diameter"]),
        )


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

    evaluation = add_d50_diagnostics(evaluation)

    evaluation = evaluation.sort_values(
        [
            "dispersion_kind",
            "oil_id",
            "experiment_id",
        ]
    ).reset_index(drop=True)

    cdf_points = build_cdf_validation_points(
        distributions=distributions,
        parameters=parameters,
    )

    fit_summary = summarize_distribution_fit_metrics(evaluation)
    fit_summary_by_regime = summarize_distribution_fit_metrics_by_regime(evaluation)
    d50_summary = summarize_d50_diagnostics(evaluation)

    return DistributionFitAnalysisResult(
        parameters=parameters.copy(),
        evaluation=evaluation,
        cdf_points=cdf_points,
        fit_summary=fit_summary,
        fit_summary_by_regime=fit_summary_by_regime,
        d50_summary=d50_summary,
    )


def run_distribution_analysis_workflow() -> DistributionFitAnalysisResult:
    parameters = load_distribution_parameters()
    distributions = load_distributions()

    result = run_distribution_fit_analysis(parameters=parameters)

    save_distribution_fit_analysis(
        evaluation=result.evaluation,
        cdf_points=result.cdf_points,
        fit_summary=result.fit_summary,
        fit_summary_by_regime=result.fit_summary_by_regime,
        d50_summary=result.d50_summary,
    )

    save_d50_parity_plot(
        evaluation=result.evaluation,
        output=(
            paths.DISTRIBUTION_ANALYSIS_FIGURES_DIR
            / "d50_fit_vs_distribution_parity.png"
        ),
    )

    save_d50_source_parity_plot(
        evaluation=result.evaluation,
        output=(
            paths.DISTRIBUTION_ANALYSIS_FIGURES_DIR
            / "d50_distribution_vs_reported_parity.png"
        ),
    )

    save_d50_relative_error_plot(
        evaluation=result.evaluation,
        output=(
            paths.DISTRIBUTION_ANALYSIS_FIGURES_DIR
            / "d50_fit_relative_error.png"
        ),
    )

    selected_cases = select_representative_fit_cases(
        result.evaluation,
        metric="cdf_rmse",
        n_each=3,
    )

    _save_representative_fit_plots(
        selected_cases=selected_cases,
        distributions=distributions,
        parameters=result.parameters,
    )

    report_distribution_analysis(
        evaluation=result.evaluation,
        d50_summary=result.d50_summary,
        fit_summary=result.fit_summary,
        selected_cases=selected_cases,
    )

    return result
