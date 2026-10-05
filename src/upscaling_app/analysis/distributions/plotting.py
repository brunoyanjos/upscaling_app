from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.analysis.distributions.rosin_rammler import (
    rosin_rammler_pdf,
)


def plot_distribution_d50_check(
    distribution: pd.DataFrame,
    measured_d50: float,
    calculated_d50: float,
    d_peak: float,
    title: str,
    output_path: Path,
) -> None:
    distribution = distribution.sort_values("droplet_diameter")

    diameter = distribution["droplet_diameter"].to_numpy(dtype=float)

    fraction = distribution["volume_fraction"].to_numpy(dtype=float)

    fraction = fraction / fraction.sum()
    cumulative = np.cumsum(fraction)

    upper_index = np.searchsorted(
        cumulative,
        0.5,
        side="left",
    )

    lower_index = max(upper_index - 1, 0)

    d0 = diameter[lower_index]
    d1 = diameter[upper_index]

    f0 = cumulative[lower_index]
    f1 = cumulative[upper_index]

    fig, (ax_dist, ax_cdf) = plt.subplots(
        2,
        1,
        figsize=(9, 8),
        sharex=True,
    )

    # Measured distribution
    ax_dist.plot(
        diameter * 1e3,
        fraction,
        marker="o",
    )

    ax_dist.axvline(
        measured_d50 * 1e3,
        linestyle="--",
        label="Measured D50",
    )

    ax_dist.axvline(
        calculated_d50 * 1e3,
        linestyle=":",
        label="Calculated D50",
    )

    ax_dist.axvline(
        d_peak * 1e3,
        linestyle="-.",
        label="Dpeak",
    )

    ax_cdf.axvline(
        d_peak * 1e3,
        linestyle="-.",
        label="Dpeak",
    )

    ax_dist.set_ylabel("Volume fraction")
    ax_dist.legend()
    ax_dist.grid(True, alpha=0.3)

    # Cumulative distribution
    ax_cdf.plot(
        diameter * 1e3,
        cumulative,
        marker="o",
    )

    ax_cdf.axhline(
        0.5,
        linestyle="--",
    )

    ax_cdf.axvline(
        measured_d50 * 1e3,
        linestyle="--",
        label="Measured D50",
    )

    ax_cdf.axvline(
        calculated_d50 * 1e3,
        linestyle=":",
        label="Calculated D50",
    )

    # Points used for interpolation
    ax_cdf.scatter(
        [d0 * 1e3, d1 * 1e3],
        [f0, f1],
        s=70,
        zorder=5,
        label="Interpolation points",
    )

    ax_cdf.set_xlabel("Droplet diameter [mm]")
    ax_cdf.set_ylabel("Cumulative volume fraction")
    ax_cdf.set_ylim(0.0, 1.05)

    ax_cdf.legend()
    ax_cdf.grid(True, alpha=0.3)

    fig.suptitle(title)

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def plot_suspicious_distributions(
    distributions: pd.DataFrame,
    comparison: pd.DataFrame,
    output_dir: Path,
    error_threshold: float = 0.05,
) -> None:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    suspicious = comparison.loc[
        comparison["d50_relative_error"].abs() > error_threshold
    ]

    for _, case in suspicious.iterrows():
        experiment_id = case["experiment_id"]

        distribution = distributions.loc[
            distributions["experiment_id"] == experiment_id
        ]

        oil_id = case["oil_id"]
        tag = case["dispersion_tag"]

        nozzle_mm = case["nozzle_diameter"] * 1e3

        gas = "gas" if case["has_gas"] else "no-gas"

        error_pct = case["d50_relative_error"] * 100.0

        title = (
            f"Oil {oil_id} | {tag} | "
            f"{nozzle_mm:.0f} mm | {gas}\n"
            f"D50 measured = {case['measured_d50'] * 1e3:.3f} mm | "
            f"D50 calc = {case['d50'] * 1e3:.3f} mm | "
            f"Dpeak = {case['d_peak'] * 1e3:.3f} mm"
        )

        filename = f"{oil_id}_" f"{tag}_" f"{nozzle_mm:.0f}mm_" f"{gas}.png"

        filename = filename.replace("/", "-")

        plot_distribution_d50_check(
            distribution=distribution,
            measured_d50=case["measured_d50"],
            calculated_d50=case["d50"],
            d_peak=case["d_peak"],
            title=title,
            output_path=output_dir / filename,
        )


def plot_distribution_cdf_comparison(
    diameter: np.ndarray,
    experimental_cdf: np.ndarray,
    rr_cdf: np.ndarray,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    diameter_mm = diameter * 1e3

    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    ax.plot(
        diameter_mm,
        experimental_cdf,
        marker="o",
        markersize=4,
        linewidth=1.5,
        label="Experimental",
    )

    ax.plot(
        diameter_mm,
        rr_cdf,
        linewidth=2.0,
        label="Rosin–Rammler",
    )

    ax.set_xlabel("Droplet diameter [mm]")

    ax.set_ylabel("Cumulative volume fraction")

    ax.set_ylim(
        0.0,
        1.0,
    )

    ax.grid(
        alpha=0.25,
    )

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
    )

    plt.close(fig)


def plot_distribution_pdf_comparison(
    edges: np.ndarray,
    experimental_density: np.ndarray,
    shape: float,
    scale: float,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    edges_mm = edges * 1e3

    experimental_density_mm = experimental_density / 1e3

    diameter_rr = np.linspace(
        edges[0],
        edges[-1],
        1000,
    )

    rr_density = rosin_rammler_pdf(
        diameter=diameter_rr,
        shape=shape,
        scale=scale,
    )

    diameter_rr_mm = diameter_rr * 1e3

    rr_density_mm = rr_density / 1e3

    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    ax.stairs(
        experimental_density_mm,
        edges_mm,
        label="Experimental",
        linewidth=1.8,
    )

    ax.plot(
        diameter_rr_mm,
        rr_density_mm,
        label="Rosin–Rammler",
        linewidth=2.0,
    )

    ax.set_xlabel("Droplet diameter [mm]")

    ax.set_ylabel(r"Volume probability density [mm$^{-1}$]")

    positive = experimental_density > 0.0

    last_positive_edge = edges_mm[np.where(positive)[0][-1] + 1]

    ax.set_xlim(
        0.0,
        last_positive_edge * 1.1,
    )

    ax.set_ylim(
        bottom=0.0,
    )

    ax.grid(
        alpha=0.25,
    )

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
    )

    plt.close(fig)


def plot_volume_number_cdf(
    diameter: np.ndarray,
    volume_cdf: np.ndarray,
    number_cdf: np.ndarray,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    diameter_mm = diameter * 1e3

    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    ax.plot(
        diameter_mm,
        volume_cdf,
        linewidth=2.0,
        label="Volume",
    )

    ax.plot(
        diameter_mm,
        number_cdf,
        linewidth=2.0,
        label="Number",
    )

    ax.set_xlabel("Droplet diameter [mm]")
    ax.set_ylabel("Cumulative fraction")

    ax.set_ylim(
        0.0,
        1.0,
    )

    ax.set_xscale("log")

    ax.grid(
        alpha=0.25,
    )

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
    )

    plt.close(fig)


def plot_number_pdf(
    edges: np.ndarray,
    density: np.ndarray,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    edges_mm = edges * 1e3
    density_mm = density / 1e3

    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    ax.stairs(
        density_mm,
        edges_mm,
        linewidth=1.8,
        label="Number",
    )

    ax.set_xlabel("Droplet diameter [mm]")
    ax.set_ylabel(r"Number probability density [mm$^{-1}$]")

    ax.set_xscale("log")

    ax.set_ylim(
        bottom=0.0,
    )

    ax.grid(
        alpha=0.25,
    )

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
    )

    plt.close(fig)


def plot_number_pdf_comparison(
    edges: np.ndarray,
    experimental_density: np.ndarray,
    rr_diameter: np.ndarray,
    rr_density: np.ndarray,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    edges_mm = edges * 1e3
    experimental_density_mm = experimental_density / 1e3

    rr_diameter_mm = rr_diameter * 1e3

    rr_density_mm = rr_density / 1e3

    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    ax.stairs(
        experimental_density_mm,
        edges_mm,
        linewidth=1.8,
        label="Experimental",
    )

    ax.plot(
        rr_diameter_mm,
        rr_density_mm,
        linewidth=2.0,
        label="Rosin–Rammler",
    )

    ax.set_xscale("log")

    ax.set_xlabel("Droplet diameter [mm]")

    ax.set_ylabel(r"Number probability density [mm$^{-1}$]")

    ax.set_ylim(
        bottom=0.0,
    )

    ax.grid(
        alpha=0.25,
    )

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
    )

    plt.close(fig)
