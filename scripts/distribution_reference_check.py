import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy.optimize import brentq
from scipy.special import gamma

from upscaling_app import paths
from upscaling_app.analysis.distributions.pipeline import (
    run_distribution_fit_workflow,
)
from upscaling_app.analysis.experimental.data import (
    load_distributions,
)
from upscaling_app.upscaling.distributions.persistence import (
    save_distribution_parameters,
)
from upscaling_app.upscaling.distributions.pipeline import (
    fit_distribution_parameters,
)

# -------------------------------------------------------------------------
# Rosin-Rammler parameters from mean and variance
# -------------------------------------------------------------------------


def _rr_from_mean_variance(
    mean: float,
    variance: float,
) -> tuple[float, float]:
    if mean <= 0.0:
        raise ValueError("Mean must be positive.")

    if variance < 0.0:
        raise ValueError("Variance must be non-negative.")

    cv_squared = variance / mean**2

    def residual(
        shape: float,
    ) -> float:
        return (
            gamma(1.0 + 2.0 / shape) / gamma(1.0 + 1.0 / shape) ** 2 - 1.0 - cv_squared
        )

    shape = brentq(
        residual,
        0.1,
        100.0,
    )

    scale = mean / gamma(1.0 + 1.0 / shape)

    return (
        float(shape),
        float(scale),
    )


# -------------------------------------------------------------------------
# Legacy backward-averaged continuous-height representation
# -------------------------------------------------------------------------


def _legacy_backward_average_moments(
    diameter: np.ndarray,
    volume_fraction: np.ndarray,
) -> tuple[float, float]:
    diameter = np.asarray(
        diameter,
        dtype=float,
    )

    volume_fraction = np.asarray(
        volume_fraction,
        dtype=float,
    )

    if diameter.size != volume_fraction.size:
        raise ValueError("diameter and volume_fraction " "must have the same size.")

    mask = np.isfinite(diameter) & np.isfinite(volume_fraction)

    diameter = diameter[mask]

    volume_fraction = volume_fraction[mask]

    if diameter.size < 3:
        raise ValueError("At least three distribution " "points are required.")

    order = np.argsort(diameter)

    diameter = diameter[order]

    volume_fraction = volume_fraction[order]

    positive = np.where(volume_fraction > 0.0)[0]

    if positive.size == 0:
        raise ValueError("Distribution has no positive weights.")

    init = max(
        int(positive[0]) - 1,
        0,
    )

    end = min(
        int(positive[-1]) + 1,
        len(volume_fraction),
    )

    weights = volume_fraction[init:end]

    d_edges = diameter[init : end + 1]

    # Reproduce the behavior of the old implementation
    # when the final boundary is missing.
    if len(d_edges) == len(weights):
        last_spacing = d_edges[-1] - d_edges[-2]

        d_edges = np.append(
            d_edges,
            d_edges[-1] + last_spacing,
        )

    if len(d_edges) != len(weights) + 1:
        raise ValueError(
            "Legacy backward-average " "representation has inconsistent lengths."
        )

    # Arithmetic midpoint used in the historical code.
    d_avg = 0.5 * (d_edges[:-1] + d_edges[1:])

    if len(d_avg) < 2:
        raise ValueError("Not enough averaged diameter points.")

    # Historical Piecewise representation:
    #
    # height = weights[i]
    #
    # over:
    #
    # d_avg[i - 1] < d <= d_avg[i]
    #
    # for i = 1, ..., n - 1.
    #
    # The expressions below analytically reproduce
    # the integrations previously done with SymPy.

    left = d_avg[:-1]

    right = d_avg[1:]

    heights = weights[1:]

    widths = right - left

    area = np.sum(heights * widths)

    if area <= 0.0:
        raise ValueError("Legacy continuous area " "must be positive.")

    first_moment_integral = np.sum(heights * 0.5 * (right**2 - left**2))

    second_moment_integral = np.sum(heights / 3.0 * (right**3 - left**3))

    mean = first_moment_integral / area

    second_moment = second_moment_integral / area

    variance = second_moment - mean**2

    if variance < 0.0 and np.isclose(
        variance,
        0.0,
    ):
        variance = 0.0

    if variance < 0.0:
        raise ValueError("Legacy variance is negative.")

    return (
        float(mean),
        float(variance),
    )


def build_legacy_moment_comparison(
    distributions: pd.DataFrame,
    parameters: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for (
        experiment_id,
        group,
    ) in distributions.groupby(
        "experiment_id",
        sort=False,
    ):
        mean, variance = _legacy_backward_average_moments(
            group["droplet_diameter"].to_numpy(dtype=float),
            group["volume_fraction"].to_numpy(dtype=float),
        )

        shape, scale = _rr_from_mean_variance(
            mean,
            variance,
        )

        d50 = scale * np.log(2.0) ** (1.0 / shape)

        rows.append(
            {
                "experiment_id": experiment_id,
                "legacy_mean": mean,
                "legacy_variance": variance,
                "legacy_shape": shape,
                "legacy_scale": scale,
                "legacy_d50": d50,
            }
        )

    legacy = pd.DataFrame(rows)

    comparison = parameters[
        [
            "experiment_id",
            "moment_shape",
            "moment_scale",
        ]
    ].merge(
        legacy,
        on="experiment_id",
        how="inner",
        validate="one_to_one",
    )

    comparison["current_d50"] = comparison["moment_scale"] * np.log(2.0) ** (
        1.0 / comparison["moment_shape"]
    )

    comparison["shape_error_pct"] = (
        (comparison["moment_shape"] - comparison["legacy_shape"])
        / comparison["legacy_shape"]
        * 100.0
    )

    comparison["scale_error_pct"] = (
        (comparison["moment_scale"] - comparison["legacy_scale"])
        / comparison["legacy_scale"]
        * 100.0
    )

    comparison["d50_error_pct"] = (
        (comparison["current_d50"] - comparison["legacy_d50"])
        / comparison["legacy_d50"]
        * 100.0
    )

    return comparison


# -------------------------------------------------------------------------
# Legacy vs current moment report
# -------------------------------------------------------------------------


def report_legacy_moment_comparison(
    comparison: pd.DataFrame,
) -> None:
    print()

    print("Current discrete moments " "vs legacy continuous-height")

    print("-" * 100)

    rows = []

    for quantity in [
        "shape",
        "scale",
        "d50",
    ]:
        error = comparison[f"{quantity}_error_pct"].abs()

        rows.append(
            {
                "quantity": quantity,
                "mean_abs_diff_pct": (error.mean()),
                "median_abs_diff_pct": (error.median()),
                "max_abs_diff_pct": (error.max()),
            }
        )

    summary = pd.DataFrame(rows)

    print(
        summary.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )


# -------------------------------------------------------------------------
# Legacy vs current D50 plot
# -------------------------------------------------------------------------


def save_legacy_moment_comparison_plot(
    comparison: pd.DataFrame,
) -> None:
    current = comparison["current_d50"] * 1e3

    legacy = comparison["legacy_d50"] * 1e3

    upper = (
        max(
            current.max(),
            legacy.max(),
        )
        * 1.05
    )

    fig, ax = plt.subplots(
        figsize=(7, 7),
    )

    ax.scatter(
        legacy,
        current,
        alpha=0.7,
        s=45,
    )

    ax.plot(
        [
            0.0,
            upper,
        ],
        [
            0.0,
            upper,
        ],
        linestyle="--",
        linewidth=1.5,
        label="Identity",
    )

    ax.set_xlim(
        0.0,
        upper,
    )

    ax.set_ylim(
        0.0,
        upper,
    )

    ax.set_aspect(
        "equal",
        adjustable="box",
    )

    ax.set_xlabel(r"Legacy continuous-height $D_{50}$ [mm]")

    ax.set_ylabel(r"Current discrete-moment $D_{50}$ [mm]")

    ax.legend()

    fig.tight_layout()

    output = (
        paths.DISTRIBUTION_ANALYSIS_FIGURES_DIR / "legacy_vs_current_moment_d50.png"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print("Legacy comparison    : " f"{output}")


# -------------------------------------------------------------------------
# Measured D50 vs all three parameter-estimation routes
# -------------------------------------------------------------------------


def save_d50_method_comparison(
    parameters: pd.DataFrame,
    legacy_comparison: pd.DataFrame,
) -> None:
    experiments = pd.read_excel(paths.EXPERIMENTS_DATABASE)

    comparison = parameters.merge(
        experiments[
            [
                "experiment_id",
                "measured_d50",
            ]
        ],
        on="experiment_id",
        how="left",
        validate="one_to_one",
    )

    comparison = comparison.merge(
        legacy_comparison[
            [
                "experiment_id",
                "legacy_d50",
            ]
        ],
        on="experiment_id",
        how="left",
        validate="one_to_one",
    )

    if (
        comparison[
            [
                "measured_d50",
                "legacy_d50",
            ]
        ]
        .isna()
        .any()
        .any()
    ):
        raise ValueError("Missing D50 values after merge.")

    ln2 = np.log(2.0)

    comparison["method_a_d50"] = comparison["cdf_scale"] * ln2 ** (
        1.0 / comparison["cdf_shape"]
    )

    comparison["current_moment_d50"] = comparison["moment_scale"] * ln2 ** (
        1.0 / comparison["moment_shape"]
    )

    measured_d50_mm = comparison["measured_d50"] * 1e3

    method_a_d50_mm = comparison["method_a_d50"] * 1e3

    current_moment_d50_mm = comparison["current_moment_d50"] * 1e3

    legacy_d50_mm = comparison["legacy_d50"] * 1e3

    upper = (
        max(
            measured_d50_mm.max(),
            method_a_d50_mm.max(),
            current_moment_d50_mm.max(),
            legacy_d50_mm.max(),
        )
        * 1.05
    )

    fig, ax = plt.subplots(
        figsize=(7, 7),
    )

    ax.scatter(
        measured_d50_mm,
        method_a_d50_mm,
        label="Method A — direct CDF fit",
        alpha=0.65,
        s=45,
    )

    ax.scatter(
        measured_d50_mm,
        current_moment_d50_mm,
        label="Current discrete moments",
        alpha=0.65,
        s=45,
    )

    ax.scatter(
        measured_d50_mm,
        legacy_d50_mm,
        label="Legacy continuous-height",
        alpha=0.65,
        s=45,
    )

    ax.plot(
        [
            0.0,
            upper,
        ],
        [
            0.0,
            upper,
        ],
        linestyle="--",
        linewidth=1.5,
        label="Identity",
    )

    ax.set_xlim(
        0.0,
        upper,
    )

    ax.set_ylim(
        0.0,
        upper,
    )

    ax.set_aspect(
        "equal",
        adjustable="box",
    )

    ax.set_xlabel(r"Measured $D_{50}$ [mm]")

    ax.set_ylabel(r"Estimated $D_{50}$ [mm]")

    ax.legend()

    fig.tight_layout()

    output = paths.DISTRIBUTION_ANALYSIS_FIGURES_DIR / "d50_method_comparison.png"

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print("D50 comparison       : " f"{output}")


# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------


def main() -> None:
    # ---------------------------------------------------------
    # Load normalized distributions
    # ---------------------------------------------------------

    distributions = load_distributions()

    # ---------------------------------------------------------
    # Fit Rosin-Rammler parameters
    #
    # Direct CDF method:
    #     nonlinear least-squares fit against measured CDF
    #
    # Current moment method:
    #     moments calculated directly from discrete
    #     volume fractions
    # ---------------------------------------------------------

    parameters = fit_distribution_parameters(distributions)

    save_distribution_parameters(parameters)

    # ---------------------------------------------------------
    # Existing distribution-fit workflow
    # ---------------------------------------------------------

    result = run_distribution_fit_workflow(parameters=parameters)

    # ---------------------------------------------------------
    # Reconstruct historical continuous-height method
    # ---------------------------------------------------------

    legacy_comparison = build_legacy_moment_comparison(
        distributions,
        parameters,
    )

    report_legacy_moment_comparison(legacy_comparison)

    save_legacy_moment_comparison_plot(legacy_comparison)

    # ---------------------------------------------------------
    # Compare all methods against measured D50
    # ---------------------------------------------------------

    save_d50_method_comparison(
        parameters,
        legacy_comparison,
    )

    # ---------------------------------------------------------
    # Basic integrity
    # ---------------------------------------------------------

    print()

    print("Fitted distributions : " f"{len(result.parameters)}")

    print("Evaluated fits       : " f"{len(result.evaluation)}")

    # ---------------------------------------------------------
    # Global fit-quality summary
    # ---------------------------------------------------------

    print()

    print("Global fit-quality summary")

    print("-" * 100)

    print(
        result.summary.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )

    # ---------------------------------------------------------
    # Paired comparison
    # ---------------------------------------------------------

    print()

    print("Paired method comparison")

    print("-" * 100)

    comparison_display = result.comparison_summary.copy()

    comparison_display["cdf_win_fraction"] *= 100.0

    comparison_display["moment_win_fraction"] *= 100.0

    print(
        comparison_display.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )

    # ---------------------------------------------------------
    # Comparison by dispersion regime
    # ---------------------------------------------------------

    print()

    print("Paired method comparison by regime")

    print("-" * 120)

    regime_display = result.comparison_by_regime.copy()

    regime_display["cdf_win_fraction"] *= 100.0

    print(
        regime_display.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )

    # ---------------------------------------------------------
    # Statistical comparison
    # ---------------------------------------------------------

    print()

    print("Paired Wilcoxon improvement test")

    print("-" * 110)

    statistical_display = result.statistical_comparison.copy()

    statistical_display["cdf_win_fraction"] *= 100.0

    print(
        statistical_display.to_string(
            index=False,
            float_format=lambda value: (f"{value:.8g}"),
        )
    )

    # ---------------------------------------------------------
    # Persisted outputs
    # ---------------------------------------------------------

    print()

    print("Persisted outputs")

    print("-" * 100)

    print("Parameters        : " f"{paths.DISTRIBUTION_PARAMETERS_PATH}")

    print("Fit evaluation    : " f"{paths.DISTRIBUTION_FIT_EVALUATION_PATH}")

    print("Method comparison : " f"{paths.DISTRIBUTION_METHOD_COMPARISON_PATH}")

    print()

    print("Figures")

    print("-" * 100)

    print(
        "Win fraction      : "
        f"{paths.DISTRIBUTION_ANALYSIS_FIGURES_DIR / 'method_win_fraction.png'}"
    )

    print(
        "Regime improvement: "
        f"{paths.DISTRIBUTION_ANALYSIS_FIGURES_DIR / 'method_improvement_by_regime.png'}"
    )

    print(
        "D50 comparison    : "
        f"{paths.DISTRIBUTION_ANALYSIS_FIGURES_DIR / 'd50_method_comparison.png'}"
    )

    print(
        "Legacy comparison : "
        f"{paths.DISTRIBUTION_ANALYSIS_FIGURES_DIR / 'legacy_vs_current_moment_d50.png'}"
    )


if __name__ == "__main__":
    main()
