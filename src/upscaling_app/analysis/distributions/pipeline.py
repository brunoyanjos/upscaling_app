from dataclasses import dataclass

import numpy as np
import pandas as pd

from upscaling_app import paths

from upscaling_app.analysis.distributions.data import (
    load_distributions,
    load_experiments,
)
from upscaling_app.analysis.distributions.descriptive import (
    discrete_moments,
    discrete_shape_statistics,
    empirical_cdf,
    empirical_quantile,
    experimental_pdf,
    summarize_distribution,
    summarize_distributions,
    volume_to_number_fraction,
)
from upscaling_app.analysis.distributions.plotting import (
    plot_distribution_cdf_comparison,
    plot_distribution_pdf_comparison,
    plot_number_pdf,
    plot_number_pdf_comparison,
    plot_suspicious_distributions,
    plot_volume_number_cdf,
)
from upscaling_app.analysis.distributions.rosin_rammler import (
    estimate_rosin_rammler_from_moments,
    rosin_rammler_cdf,
    rosin_rammler_moments,
    rosin_rammler_pdf,
    rosin_rammler_quantile,
    rosin_rammler_shape_statistics,
)
from upscaling_app.analysis.distributions.validation import (
    add_reported_d50_percentile,
    cdf_error_metrics,
    compare_distribution_d50,
)


@dataclass(frozen=True)
class DistributionAnalysisResult:
    data: pd.DataFrame
    summary: pd.DataFrame
    d50_comparison: pd.DataFrame


@dataclass(frozen=True)
class DistributionReferenceResult:
    experiment: pd.Series
    distribution: pd.DataFrame
    summary: pd.Series

    # Volume-based Rosin-Rammler
    rr_shape: float
    rr_scale: float
    rr_mean: float
    rr_std: float
    rr_d10: float
    rr_d50: float
    rr_d90: float

    experimental_skewness: float
    experimental_kurtosis: float
    rr_skewness: float
    rr_kurtosis: float

    experimental_cdf: np.ndarray
    rr_cdf: np.ndarray
    cdf_rmse: float
    cdf_max_error: float
    cdf_max_error_index: int

    pdf_edges: np.ndarray
    experimental_density: np.ndarray
    pdf_integral: float

    # Number-based experimental distribution
    number_fraction: np.ndarray
    number_mean: float
    number_std: float
    number_d10: float
    number_d50: float
    number_d90: float
    d50_number_to_volume: float

    number_cdf: np.ndarray
    number_pdf_edges: np.ndarray
    number_density: np.ndarray
    number_pdf_integral: float

    # Number-based Rosin-Rammler
    number_rr_shape: float
    number_rr_scale: float
    number_rr_mean: float
    number_rr_std: float
    number_rr_d10: float
    number_rr_d50: float
    number_rr_d90: float

    number_rr_cdf: np.ndarray
    number_cdf_rmse: float
    number_cdf_max_error: float
    number_cdf_max_error_index: int

    number_rr_diameter: np.ndarray
    number_rr_density: np.ndarray


def run_distribution_analysis() -> DistributionAnalysisResult:
    distributions = load_distributions()
    experiments = load_experiments()

    summary = summarize_distributions(
        distributions,
    )

    d50_comparison = compare_distribution_d50(
        summary,
        experiments,
    )

    d50_comparison = add_reported_d50_percentile(
        comparison=d50_comparison,
        distributions=distributions,
    )

    return DistributionAnalysisResult(
        data=distributions,
        summary=summary,
        d50_comparison=d50_comparison,
    )


def run_distribution_workflow() -> DistributionAnalysisResult:
    result = run_distribution_analysis()

    plot_suspicious_distributions(
        distributions=result.data,
        comparison=result.d50_comparison,
        output_dir=(paths.RESULTS_DIR / "distributions" / "d50_checks"),
    )

    return result


def run_distribution_reference_analysis(
    experiment_id: str,
) -> DistributionReferenceResult:
    distributions = load_distributions()
    experiments = load_experiments()

    distribution = distributions[distributions["experiment_id"] == experiment_id]

    experiment = experiments[experiments["experiment_id"] == experiment_id]

    if distribution.empty:
        raise ValueError(f"Distribution not found for {experiment_id}.")

    if experiment.empty:
        raise ValueError(f"Experiment not found for {experiment_id}.")

    experiment = experiment.iloc[0]

    distribution = distribution.sort_values("droplet_diameter")

    diameter = distribution["droplet_diameter"].to_numpy(dtype=float)

    fraction = distribution["volume_fraction"].to_numpy(dtype=float)

    # =========================================================
    # Experimental volume-based reference
    # =========================================================

    summary = summarize_distribution(distribution)

    mean = summary["mean_diameter"]
    std = summary["std_diameter"]

    (
        experimental_skewness,
        experimental_kurtosis,
    ) = discrete_shape_statistics(
        diameter=diameter,
        fraction=fraction,
    )

    experimental_cdf = empirical_cdf(fraction)

    (
        _,
        pdf_edges,
        experimental_density,
    ) = experimental_pdf(
        diameter=diameter,
        fraction=fraction,
    )

    pdf_widths = np.diff(pdf_edges)

    pdf_integral = float(np.sum(experimental_density * pdf_widths))

    # =========================================================
    # Rosin-Rammler — volume basis
    # =========================================================

    shape, scale = estimate_rosin_rammler_from_moments(
        mean=mean,
        std=std,
    )

    rr_mean, rr_std = rosin_rammler_moments(
        shape=shape,
        scale=scale,
    )

    rr_d10 = rosin_rammler_quantile(
        quantile=0.10,
        shape=shape,
        scale=scale,
    )

    rr_d50 = rosin_rammler_quantile(
        quantile=0.50,
        shape=shape,
        scale=scale,
    )

    rr_d90 = rosin_rammler_quantile(
        quantile=0.90,
        shape=shape,
        scale=scale,
    )

    (
        rr_skewness,
        rr_kurtosis,
    ) = rosin_rammler_shape_statistics(
        shape=shape,
        scale=scale,
    )

    rr_cdf = rosin_rammler_cdf(
        diameter=diameter,
        shape=shape,
        scale=scale,
    )

    (
        cdf_rmse,
        cdf_max_error,
        cdf_max_error_index,
    ) = cdf_error_metrics(
        reference=experimental_cdf,
        prediction=rr_cdf,
    )

    # =========================================================
    # Experimental number-based representation
    # =========================================================

    number_fraction = volume_to_number_fraction(
        diameter=diameter,
        volume_fraction=fraction,
    )

    (
        number_mean,
        _,
        number_std,
    ) = discrete_moments(
        diameter=diameter,
        fraction=number_fraction,
    )

    number_d10 = empirical_quantile(
        diameter=diameter,
        fraction=number_fraction,
        quantile=0.10,
    )

    number_d50 = empirical_quantile(
        diameter=diameter,
        fraction=number_fraction,
        quantile=0.50,
    )

    number_d90 = empirical_quantile(
        diameter=diameter,
        fraction=number_fraction,
        quantile=0.90,
    )

    d50_number_to_volume = number_d50 / summary["d50"]

    number_cdf = empirical_cdf(number_fraction)

    (
        _,
        number_pdf_edges,
        number_density,
    ) = experimental_pdf(
        diameter=diameter,
        fraction=number_fraction,
    )

    number_pdf_widths = np.diff(number_pdf_edges)

    number_pdf_integral = float(np.sum(number_density * number_pdf_widths))

    # =========================================================
    # Rosin-Rammler — number basis
    # =========================================================

    (
        number_rr_shape,
        number_rr_scale,
    ) = estimate_rosin_rammler_from_moments(
        mean=number_mean,
        std=number_std,
    )

    (
        number_rr_mean,
        number_rr_std,
    ) = rosin_rammler_moments(
        shape=number_rr_shape,
        scale=number_rr_scale,
    )

    number_rr_d10 = rosin_rammler_quantile(
        quantile=0.10,
        shape=number_rr_shape,
        scale=number_rr_scale,
    )

    number_rr_d50 = rosin_rammler_quantile(
        quantile=0.50,
        shape=number_rr_shape,
        scale=number_rr_scale,
    )

    number_rr_d90 = rosin_rammler_quantile(
        quantile=0.90,
        shape=number_rr_shape,
        scale=number_rr_scale,
    )

    number_rr_cdf = rosin_rammler_cdf(
        diameter=diameter,
        shape=number_rr_shape,
        scale=number_rr_scale,
    )

    (
        number_cdf_rmse,
        number_cdf_max_error,
        number_cdf_max_error_index,
    ) = cdf_error_metrics(
        reference=number_cdf,
        prediction=number_rr_cdf,
    )

    number_rr_diameter = np.geomspace(
        number_pdf_edges[0],
        number_pdf_edges[-1],
        1000,
    )

    number_rr_density = rosin_rammler_pdf(
        diameter=number_rr_diameter,
        shape=number_rr_shape,
        scale=number_rr_scale,
    )

    return DistributionReferenceResult(
        experiment=experiment,
        distribution=distribution,
        summary=summary,
        # Volume RR
        rr_shape=shape,
        rr_scale=scale,
        rr_mean=rr_mean,
        rr_std=rr_std,
        rr_d10=rr_d10,
        rr_d50=rr_d50,
        rr_d90=rr_d90,
        experimental_skewness=experimental_skewness,
        experimental_kurtosis=experimental_kurtosis,
        rr_skewness=rr_skewness,
        rr_kurtosis=rr_kurtosis,
        experimental_cdf=experimental_cdf,
        rr_cdf=rr_cdf,
        cdf_rmse=cdf_rmse,
        cdf_max_error=cdf_max_error,
        cdf_max_error_index=cdf_max_error_index,
        pdf_edges=pdf_edges,
        experimental_density=experimental_density,
        pdf_integral=pdf_integral,
        # Number experimental
        number_fraction=number_fraction,
        number_mean=number_mean,
        number_std=number_std,
        number_d10=number_d10,
        number_d50=number_d50,
        number_d90=number_d90,
        d50_number_to_volume=d50_number_to_volume,
        number_cdf=number_cdf,
        number_pdf_edges=number_pdf_edges,
        number_density=number_density,
        number_pdf_integral=number_pdf_integral,
        # Number RR
        number_rr_shape=number_rr_shape,
        number_rr_scale=number_rr_scale,
        number_rr_mean=number_rr_mean,
        number_rr_std=number_rr_std,
        number_rr_d10=number_rr_d10,
        number_rr_d50=number_rr_d50,
        number_rr_d90=number_rr_d90,
        number_rr_cdf=number_rr_cdf,
        number_cdf_rmse=number_cdf_rmse,
        number_cdf_max_error=number_cdf_max_error,
        number_cdf_max_error_index=number_cdf_max_error_index,
        number_rr_diameter=number_rr_diameter,
        number_rr_density=number_rr_density,
    )


def run_distribution_reference_workflow(
    experiment_id: str,
) -> DistributionReferenceResult:
    result = run_distribution_reference_analysis(experiment_id)

    diameter = result.distribution["droplet_diameter"].to_numpy(dtype=float)

    output_dir = paths.RESULTS_DIR / "distributions" / "reference_check"

    # =========================================================
    # Volume-based diagnostics
    # =========================================================

    plot_distribution_cdf_comparison(
        diameter=diameter,
        experimental_cdf=result.experimental_cdf,
        rr_cdf=result.rr_cdf,
        output=(output_dir / f"{experiment_id}_volume_cdf.png"),
    )

    plot_distribution_pdf_comparison(
        edges=result.pdf_edges,
        experimental_density=result.experimental_density,
        shape=result.rr_shape,
        scale=result.rr_scale,
        output=(output_dir / f"{experiment_id}_volume_pdf.png"),
    )

    # =========================================================
    # Volume vs number
    # =========================================================

    plot_volume_number_cdf(
        diameter=diameter,
        volume_cdf=result.experimental_cdf,
        number_cdf=result.number_cdf,
        output=(output_dir / f"{experiment_id}_volume_number_cdf.png"),
    )

    # =========================================================
    # Number-based diagnostics
    # =========================================================

    plot_number_pdf(
        edges=result.number_pdf_edges,
        density=result.number_density,
        output=(output_dir / f"{experiment_id}_number_pdf.png"),
    )

    plot_number_pdf_comparison(
        edges=result.number_pdf_edges,
        experimental_density=result.number_density,
        rr_diameter=result.number_rr_diameter,
        rr_density=result.number_rr_density,
        output=(output_dir / f"{experiment_id}_number_rr_pdf.png"),
    )

    return result
