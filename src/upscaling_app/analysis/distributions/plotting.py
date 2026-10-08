from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.plotting.colors import get_gray
from upscaling_app.plotting.style import apply_plot_style


def save_pdf_fit(
    edges: np.ndarray,
    experimental_density: np.ndarray,
    rr_diameter: np.ndarray,
    fitted_density: np.ndarray,
    output: Path,
    *,
    experimental_color: str,
    plot_max_diameter: float,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    ax.stairs(
        experimental_density / 1e3,
        edges * 1e3,
        color=experimental_color,
        linewidth=2.2,
        label="Experimental",
        zorder=3,
    )

    ax.plot(
        rr_diameter * 1e3,
        fitted_density / 1e3,
        color=get_gray("regression"),
        linewidth=2.2,
        label="Rosin–Rammler fit",
        zorder=2,
    )

    ax.set_xlabel("Droplet diameter [mm]")
    ax.set_ylabel(r"Volume density [mm$^{-1}$]")
    ax.set_xlim(0.0, plot_max_diameter * 1e3)
    ax.set_ylim(bottom=0.0)

    ax.grid(
        color=get_gray("grid"),
        alpha=0.8,
    )

    ax.legend()

    fig.tight_layout()
    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def save_cdf_fit(
    diameter: np.ndarray,
    experimental_cdf: np.ndarray,
    fitted_cdf_at_data: np.ndarray,
    rr_diameter: np.ndarray,
    fitted_cdf: np.ndarray,
    output: Path,
    *,
    experimental_color: str,
    plot_max_diameter: float,
) -> None:
    """Save the experimental CDF and its Rosin–Rammler reconstruction.

    ``fitted_cdf_at_data`` is retained in the function signature for compatibility
    with the current pipeline. It is intentionally not plotted because those
    values are samples of the same continuous Rosin–Rammler curve and therefore
    do not represent an independent data series.
    """
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Keep the existing pipeline contract without introducing a redundant
    # visual series in the figure.
    _ = fitted_cdf_at_data

    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    ax.scatter(
        diameter * 1e3,
        experimental_cdf,
        s=38,
        color=experimental_color,
        label="Experimental",
        zorder=3,
    )

    ax.plot(
        rr_diameter * 1e3,
        fitted_cdf,
        color=get_gray("regression"),
        linewidth=2.2,
        label="Rosin–Rammler fit",
        zorder=2,
    )

    ax.set_xlabel("Droplet diameter [mm]")
    ax.set_ylabel("Cumulative volume fraction [-]")
    ax.set_xlim(0.0, plot_max_diameter * 1e3)
    ax.set_ylim(0.0, 1.02)

    ax.grid(
        color=get_gray("grid"),
        alpha=0.8,
    )

    ax.legend()

    fig.tight_layout()
    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def _parity_limits(
    reference: np.ndarray,
    estimate: np.ndarray,
) -> tuple[float, float]:
    upper = 1.05 * max(
        float(np.max(reference)),
        float(np.max(estimate)),
    )

    return 0.0, upper


def save_d50_parity_plot(
    evaluation: pd.DataFrame,
    output: Path,
) -> None:
    """Parity of fitted D50 against the distribution-reconstructed D50."""
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    reference = evaluation["distribution_d50"].to_numpy(dtype=float) * 1e3
    estimated = evaluation["fitted_d50"].to_numpy(dtype=float) * 1e3

    lower, upper = _parity_limits(
        reference,
        estimated,
    )

    fig, ax = plt.subplots(
        figsize=(8, 8),
    )

    ax.scatter(
        reference,
        estimated,
        s=45,
        alpha=0.75,
        color=get_gray("dark"),
        label="Rosin–Rammler fit",
        zorder=3,
    )

    ax.plot(
        [lower, upper],
        [lower, upper],
        linestyle="--",
        linewidth=1.8,
        color=get_gray("identity"),
        label="Identity",
        zorder=2,
    )

    ax.set_xlabel(r"Distribution-reconstructed $D_{50}$ [mm]")
    ax.set_ylabel(r"Fitted $D_{50}$ [mm]")
    ax.set_xlim(lower, upper)
    ax.set_ylim(lower, upper)
    ax.set_aspect(
        "equal",
        adjustable="box",
    )

    ax.grid(
        color=get_gray("grid"),
        alpha=0.8,
    )

    ax.legend()

    fig.tight_layout()
    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def save_d50_source_parity_plot(
    evaluation: pd.DataFrame,
    output: Path,
) -> None:
    """Diagnostic parity between reported and distribution-reconstructed D50."""
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    reported = evaluation["measured_d50"].to_numpy(dtype=float) * 1e3
    reconstructed = evaluation["distribution_d50"].to_numpy(dtype=float) * 1e3

    lower, upper = _parity_limits(
        reported,
        reconstructed,
    )

    fig, ax = plt.subplots(
        figsize=(8, 8),
    )

    ax.scatter(
        reported,
        reconstructed,
        s=45,
        alpha=0.75,
        color=get_gray("dark"),
        label="Distribution reconstruction",
        zorder=3,
    )

    ax.plot(
        [lower, upper],
        [lower, upper],
        linestyle="--",
        linewidth=1.8,
        color=get_gray("identity"),
        label="Identity",
        zorder=2,
    )

    ax.set_xlabel(r"Reported $D_{50}$ [mm]")
    ax.set_ylabel(r"Distribution-reconstructed $D_{50}$ [mm]")
    ax.set_xlim(lower, upper)
    ax.set_ylim(lower, upper)
    ax.set_aspect(
        "equal",
        adjustable="box",
    )

    ax.grid(
        color=get_gray("grid"),
        alpha=0.8,
    )

    ax.legend()

    fig.tight_layout()
    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def save_d50_relative_error_plot(
    evaluation: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    reference = evaluation["distribution_d50"].to_numpy(dtype=float) * 1e3
    relative_error = evaluation["fit_d50_relative_error"].to_numpy(dtype=float) * 100.0

    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    ax.scatter(
        reference,
        relative_error,
        s=45,
        alpha=0.75,
        color=get_gray("dark"),
        zorder=3,
    )

    ax.axhline(
        0.0,
        linestyle="--",
        linewidth=1.8,
        color=get_gray("identity"),
        zorder=2,
    )

    ax.set_xlabel(r"Distribution-reconstructed $D_{50}$ [mm]")
    ax.set_ylabel(r"Fitted $D_{50}$ relative error [%]")

    ax.grid(
        color=get_gray("grid"),
        alpha=0.8,
    )

    fig.tight_layout()
    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)
