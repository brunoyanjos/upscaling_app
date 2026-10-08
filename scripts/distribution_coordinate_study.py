"""Compare Rosin–Rammler fitting conventions without changing production outputs.

Run from the repository root:
    python scripts/distribution_coordinate_study.py

The script only reads normalized databases and writes into:
    data/results/research/distribution_coordinates/

Methods
-------
point   : direct CDF fit evaluated at original droplet diameters
upper   : direct CDF fit evaluated at geometric upper bin edges
moments : discrete-moment estimator using original droplet diameters
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.analysis.experimental.data import (
    load_distributions,
    load_experiments,
)
from upscaling_app.upscaling.distributions.fitting import (
    fit_rosin_rammler,
    fit_rosin_rammler_from_moments,
)
from upscaling_app.upscaling.distributions.representation import (
    empirical_cdf,
    experimental_pdf,
    geometric_bin_edges,
)
from upscaling_app.upscaling.distributions.rosin_rammler import (
    rosin_rammler_cdf,
    rosin_rammler_pdf,
    rosin_rammler_quantile,
)

OUTPUT_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "results"
    / "research"
    / "distribution_coordinates"
)

METHODS = ("point", "upper", "moments")


def rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    if actual.shape != predicted.shape:
        raise ValueError("RMSE inputs must have the same shape.")

    return float(np.sqrt(np.mean((predicted - actual) ** 2)))


def empirical_d50(
    diameter: np.ndarray,
    cumulative: np.ndarray,
) -> float:
    """Interpolate F=0.5 on the original diameter coordinates."""
    index = int(np.searchsorted(cumulative, 0.5, side="left"))

    if index == 0:
        return float(diameter[0])
    if index >= len(diameter):
        return float(diameter[-1])

    d0, d1 = diameter[index - 1], diameter[index]
    f0, f1 = cumulative[index - 1], cumulative[index]

    if np.isclose(f0, f1):
        return float(d1)

    return float(d0 + (0.5 - f0) * (d1 - d0) / (f1 - f0))


def evaluate_method(
    diameter: np.ndarray,
    edges: np.ndarray,
    fraction: np.ndarray,
    cumulative: np.ndarray,
    fitting_diameter: np.ndarray,
    *,
    parameters: tuple[float, float] | None = None,
) -> dict[str, float]:
    """Estimate/accept parameters and score on fixed comparison grids."""
    if parameters is None:
        shape, scale = fit_rosin_rammler(
            diameter=fitting_diameter,
            cumulative_fraction=cumulative,
        )
    else:
        shape, scale = parameters

    shape, scale = float(shape), float(scale)

    # The direct CDF estimator is scored on the coordinates it was fitted on.
    predicted_own = rosin_rammler_cdf(fitting_diameter, shape, scale)

    # Common CDF coordinates, irrespective of which method fitted the model.
    predicted_point = rosin_rammler_cdf(diameter, shape, scale)
    predicted_upper = rosin_rammler_cdf(edges[1:], shape, scale)

    # Common physical bin edges for all methods (52 bins -> 53 edges).
    predicted_bin_mass = np.diff(rosin_rammler_cdf(edges, shape, scale))
    observed_bin_mass = fraction / fraction.sum()

    mass_in_window = float(predicted_bin_mass.sum())
    if not np.isfinite(mass_in_window) or mass_in_window <= 0.0:
        raise ValueError("Model assigns no finite probability to measured bins.")

    normalized_predicted_bin_mass = predicted_bin_mass / mass_in_window

    return {
        "shape": shape,
        "scale": scale,
        "d50": float(rosin_rammler_quantile(0.5, shape, scale)),
        "cdf_rmse_own": rmse(cumulative, predicted_own),
        "cdf_rmse_original": rmse(cumulative, predicted_point),
        "cdf_rmse_upper": rmse(cumulative, predicted_upper),
        "bin_mass_rmse": rmse(observed_bin_mass, normalized_predicted_bin_mass),
        "bin_mass_rmse_raw": rmse(observed_bin_mass, predicted_bin_mass),
        "mass_outside": 1.0 - mass_in_window,
    }


def evaluate_all(
    distributions: pd.DataFrame,
    experiments: pd.DataFrame,
) -> pd.DataFrame:
    metadata = experiments.set_index("experiment_id")
    if not metadata.index.is_unique:
        raise ValueError("Duplicated experiment IDs in experiments database.")

    rows = []

    for experiment_id, data in distributions.groupby("experiment_id", sort=True):
        if experiment_id not in metadata.index:
            raise ValueError(f"Missing metadata for experiment {experiment_id}.")

        data = data.sort_values("droplet_diameter")
        diameter = data["droplet_diameter"].to_numpy(dtype=float)
        fraction = data["volume_fraction"].to_numpy(dtype=float)

        cumulative = empirical_cdf(fraction)
        edges = geometric_bin_edges(diameter)

        point = evaluate_method(diameter, edges, fraction, cumulative, diameter)
        upper = evaluate_method(diameter, edges, fraction, cumulative, edges[1:])

        moment_parameters = fit_rosin_rammler_from_moments(
            diameter=diameter,
            volume_fraction=fraction,
        )
        moments = evaluate_method(
            diameter,
            edges,
            fraction,
            cumulative,
            diameter,
            parameters=moment_parameters,
        )

        meta = metadata.loc[experiment_id]
        measured_d50 = float(meta["measured_d50"])
        distribution_d50 = empirical_d50(diameter, cumulative)

        if measured_d50 <= 0.0 or distribution_d50 <= 0.0:
            raise ValueError(f"Invalid D50 for experiment {experiment_id}.")

        row = {
            "experiment_id": experiment_id,
            "oil_id": int(meta["oil_id"]),
            "dispersion_kind": meta["dispersion_kind"],
            "dispersion_tag": meta["dispersion_tag"],
            "nozzle_diameter": float(meta["nozzle_diameter"]),
            "has_gas": bool(meta["has_gas"]),
            "measured_d50": measured_d50,
            "distribution_d50": distribution_d50,
        }

        for name, values in (
            ("point", point),
            ("upper", upper),
            ("moments", moments),
        ):
            for metric, value in values.items():
                row[f"{name}_{metric}"] = value

            row[f"{name}_d50_error_pct"] = (
                100.0 * (values["d50"] - measured_d50) / measured_d50
            )
            row[f"{name}_distribution_d50_error_pct"] = (
                100.0 * (values["d50"] - distribution_d50) / distribution_d50
            )

        # Negative: point has lower mass error. Positive: upper has lower error.
        row["bin_mass_rmse_delta"] = point["bin_mass_rmse"] - upper["bin_mass_rmse"]
        row["scale_ratio_upper_point"] = upper["scale"] / point["scale"]
        row["shape_difference"] = point["shape"] - upper["shape"]
        rows.append(row)

    return pd.DataFrame(rows)


def summarize_fit_metrics(results: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for method in METHODS:
        rows.append(
            {
                "method": method,
                "n": len(results),
                "mean_cdf_rmse_own": results[f"{method}_cdf_rmse_own"].mean(),
                "mean_cdf_rmse_original": results[f"{method}_cdf_rmse_original"].mean(),
                "mean_cdf_rmse_upper": results[f"{method}_cdf_rmse_upper"].mean(),
                "mean_bin_mass_rmse": results[f"{method}_bin_mass_rmse"].mean(),
                "mean_bin_mass_rmse_raw": results[f"{method}_bin_mass_rmse_raw"].mean(),
                "mean_mass_outside_pct": (
                    100.0 * results[f"{method}_mass_outside"].mean()
                ),
            }
        )
    return pd.DataFrame(rows)


def summarize_d50_metrics(results: pd.DataFrame) -> pd.DataFrame:
    rows = []
    references = {
        "reported": "measured_d50",
        "distribution": "distribution_d50",
    }

    for reference_name, reference_column in references.items():
        observed = results[reference_column].to_numpy(dtype=float)
        if not np.all(np.isfinite(observed)) or np.any(observed <= 0.0):
            raise ValueError(f"Invalid D50 reference: {reference_column}.")

        log_observed = np.log(observed)
        sst = float(np.sum((observed - observed.mean()) ** 2))
        sst_log = float(np.sum((log_observed - log_observed.mean()) ** 2))

        for method in METHODS:
            predicted = results[f"{method}_d50"].to_numpy(dtype=float)
            if not np.all(np.isfinite(predicted)) or np.any(predicted <= 0.0):
                raise ValueError(f"Invalid {method} D50 predictions.")

            error = predicted - observed
            absolute_relative_error = np.abs(error / observed)
            log_error = np.log(predicted) - log_observed

            rows.append(
                {
                    "reference": reference_name,
                    "method": method,
                    "n": len(observed),
                    "rmse_mm": float(np.sqrt(np.mean(error**2)) * 1e3),
                    "mae_mm": float(np.mean(np.abs(error)) * 1e3),
                    "mape_pct": float(100.0 * np.mean(absolute_relative_error)),
                    "median_ape_pct": float(100.0 * np.median(absolute_relative_error)),
                    "bias_mm": float(np.mean(error) * 1e3),
                    "r2": float(1.0 - np.sum(error**2) / sst) if sst > 0.0 else np.nan,
                    "log_mse": float(np.mean(log_error**2)),
                    "r2_log": (
                        float(1.0 - np.sum(log_error**2) / sst_log)
                        if sst_log > 0.0
                        else np.nan
                    ),
                }
            )

    return pd.DataFrame(rows)


def select_cases(results: pd.DataFrame) -> pd.DataFrame:
    """Pick three lowest/middle/highest point-minus-upper mass gaps."""
    ranked = results.sort_values(["bin_mass_rmse_delta", "experiment_id"]).reset_index(
        drop=True
    )

    if len(ranked) < 9:
        raise ValueError("At least 9 experiments are required.")

    middle = len(ranked) // 2
    groups = (
        ("lowest_delta", ranked.head(3)),
        ("middle_delta", ranked.iloc[middle - 1 : middle + 2]),
        ("highest_delta", ranked.tail(3).iloc[::-1]),
    )

    selected = []
    for group, subset in groups:
        part = subset.copy()
        part["case_group"] = group
        part["case_rank"] = np.arange(1, len(part) + 1)
        selected.append(part)

    return pd.concat(selected, ignore_index=True)


def plot_d50_parity(
    results: pd.DataFrame,
    reference_column: str,
) -> None:
    label = {
        "measured_d50": "Reported",
        "distribution_d50": "Distribution-reconstructed",
    }[reference_column]

    reference = results[reference_column].to_numpy(dtype=float) * 1e3
    series = {
        "Original diameters": ("point", "o"),
        "Upper edges": ("upper", "s"),
        "Discrete moments": ("moments", "^"),
    }

    upper_limit = 1.05 * max(
        reference.max(),
        *(results[f"{name}_d50"].max() * 1e3 for name in METHODS),
    )

    fig, ax = plt.subplots(figsize=(7, 7))
    for name, (method, marker) in series.items():
        predicted = results[f"{method}_d50"].to_numpy(dtype=float) * 1e3
        ax.scatter(reference, predicted, alpha=0.65, s=32, marker=marker, label=name)

    ax.plot(
        [0, upper_limit],
        [0, upper_limit],
        linestyle="--",
        color="gray",
        label="Identity",
    )
    ax.set_xlabel(rf"{label} $D_{{50}}$ [mm]")
    ax.set_ylabel(r"Estimated $D_{50}$ [mm]")
    ax.set_xlim(0, upper_limit)
    ax.set_ylim(0, upper_limit)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"d50_parity_{reference_column}.png", dpi=300)
    plt.close(fig)


def plot_selected_cases(
    selected: pd.DataFrame,
    distributions: pd.DataFrame,
) -> None:
    figure_dir = OUTPUT_DIR / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    grouped = distributions.groupby("experiment_id")

    for case in selected.itertuples(index=False):
        data = grouped.get_group(case.experiment_id)
        data = data.sort_values("droplet_diameter")

        diameter = data["droplet_diameter"].to_numpy(dtype=float)
        fraction = data["volume_fraction"].to_numpy(dtype=float)
        cumulative = empirical_cdf(fraction)
        edges, experimental_density = experimental_pdf(
            diameter=diameter,
            volume_fraction=fraction,
        )

        model_quantiles = [
            float(
                rosin_rammler_quantile(
                    0.99,
                    getattr(case, f"{method}_shape"),
                    getattr(case, f"{method}_scale"),
                )
            )
            for method in METHODS
        ]
        active = fraction > 0.0
        if not active.any():
            raise ValueError(f"Empty distribution: {case.experiment_id}.")
        last_active_edge = edges[1:][active][-1]
        plot_max = 1.1 * max(last_active_edge, *model_quantiles)
        smooth = np.geomspace(edges[0], max(edges[-1], plot_max), 600)

        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        axes[0].plot(
            diameter * 1e3, cumulative, "o", markersize=3, label="Experimental"
        )
        axes[1].stairs(experimental_density / 1e3, edges * 1e3, label="Experimental")

        for method, label in (
            ("point", "Direct CDF — original diameters"),
            ("upper", "Direct CDF — upper edges"),
            ("moments", "Discrete moments"),
        ):
            shape = float(getattr(case, f"{method}_shape"))
            scale = float(getattr(case, f"{method}_scale"))
            axes[0].plot(
                smooth * 1e3,
                rosin_rammler_cdf(smooth, shape, scale),
                label=label,
            )
            axes[1].plot(
                smooth * 1e3,
                rosin_rammler_pdf(smooth, shape, scale) / 1e3,
                label=label,
            )

        for ax in axes:
            ax.set_xlim(0, plot_max * 1e3)
            ax.set_xlabel("Droplet diameter [mm]")
            ax.grid(alpha=0.3)
            ax.legend()

        axes[0].set_ylabel("Cumulative volume fraction [-]")
        axes[0].set_ylim(0, 1.02)
        axes[1].set_ylabel("Volume density [mm⁻¹]")

        fig.tight_layout()
        filename = (
            f"{case.case_group}_{int(case.case_rank):02d}_"
            f"oil_{int(case.oil_id)}_{str(case.experiment_id)[:8]}.png"
        )
        fig.savefig(figure_dir / filename, dpi=300)
        plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    distributions = load_distributions()
    experiments = load_experiments()

    results = evaluate_all(distributions, experiments)
    fit_summary = summarize_fit_metrics(results)
    d50_summary = summarize_d50_metrics(results)
    selected = select_cases(results)

    results.to_csv(OUTPUT_DIR / "comparison.csv", index=False)
    fit_summary.to_csv(OUTPUT_DIR / "summary.csv", index=False)
    d50_summary.to_csv(OUTPUT_DIR / "d50_metrics.csv", index=False)
    selected.to_csv(OUTPUT_DIR / "selected_cases.csv", index=False)

    plot_d50_parity(results, "measured_d50")
    plot_d50_parity(results, "distribution_d50")
    plot_selected_cases(selected, distributions)

    print("\nDistribution coordinate study")
    print("=" * 80)
    print(f"Experiments: {len(results)}")
    print("\nFit-quality metrics")
    print(fit_summary.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("\nD50 agreement metrics")
    print(d50_summary.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print(
        "\nMean scale ratio (upper/point):",
        f"{results['scale_ratio_upper_point'].mean():.6f}",
    )
    print(
        "Point better in bin-mass RMSE:",
        int((results["bin_mass_rmse_delta"] < 0).sum()),
    )
    print(
        "Upper better in bin-mass RMSE:",
        int((results["bin_mass_rmse_delta"] > 0).sum()),
    )
    print(
        "\nPoint CDF fit worse than moments on original diameter:",
        int(
            (
                results["point_cdf_rmse_original"]
                > results["moments_cdf_rmse_original"] + 1e-8
            ).sum()
        ),
    )
    print(f"\nResults: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
