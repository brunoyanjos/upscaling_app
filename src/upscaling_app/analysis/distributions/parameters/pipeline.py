from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.distributions.parameters.analysis import (
    attach_distribution_fit_quality,
    prepare_distribution_parameter_data,
    select_shape_extremes,
    summarize_distribution_parameters,
)
from upscaling_app.analysis.distributions.parameters.plotting import (
    save_scale_by_regime_plot,
    save_shape_by_regime_plot,
    save_shape_vs_fit_quality_plot,
    save_shape_vs_rr_d50_plot,
)
from upscaling_app.analysis.experimental.data import (
    load_experiments,
)


@dataclass(frozen=True)
class DistributionParameterAnalysisResult:
    data: pd.DataFrame
    summary: pd.DataFrame
    shape_extremes: pd.DataFrame


def load_distribution_parameters() -> pd.DataFrame:
    path = paths.DISTRIBUTION_PARAMETERS_PATH

    if not path.exists():
        raise FileNotFoundError("Distribution parameter file not found: " f"{path}")

    parameters = pd.read_excel(path)

    if parameters.empty:
        raise ValueError("Distribution parameter file is empty.")

    return parameters


def load_distribution_fit_evaluation() -> pd.DataFrame:
    path = paths.DISTRIBUTION_FIT_EVALUATION_PATH

    if not path.exists():
        raise FileNotFoundError(
            "Distribution fit-evaluation file not found: " f"{path}"
        )

    evaluation = pd.read_excel(path)

    if evaluation.empty:
        raise ValueError("Distribution fit-evaluation file is empty.")

    return evaluation


def run_distribution_parameter_analysis() -> DistributionParameterAnalysisResult:
    parameters = load_distribution_parameters()
    experiments = load_experiments()
    evaluation = load_distribution_fit_evaluation()

    data = prepare_distribution_parameter_data(
        parameters=parameters,
        experiments=experiments,
    )

    data = attach_distribution_fit_quality(
        data=data,
        evaluation=evaluation,
    )

    summary = summarize_distribution_parameters(data)

    shape_extremes = select_shape_extremes(
        data=data,
        n=10,
    )

    return DistributionParameterAnalysisResult(
        data=data,
        summary=summary,
        shape_extremes=shape_extremes,
    )


def run_distribution_parameter_workflow() -> DistributionParameterAnalysisResult:
    result = run_distribution_parameter_analysis()

    save_shape_by_regime_plot(
        data=result.data,
        output=(paths.DISTRIBUTION_PARAMETER_FIGURES_DIR / "shape_by_regime.png"),
    )

    save_shape_vs_fit_quality_plot(
        data=result.data,
        output=(paths.DISTRIBUTION_PARAMETER_FIGURES_DIR / "shape_vs_fit_quality.png"),
    )

    save_scale_by_regime_plot(
        data=result.data,
        output=(paths.DISTRIBUTION_PARAMETER_FIGURES_DIR / "scale_by_regime.png"),
    )

    save_shape_vs_rr_d50_plot(
        data=result.data,
        output=(paths.DISTRIBUTION_PARAMETER_FIGURES_DIR / "shape_vs_rr_d50.png"),
    )

    return result
