from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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
