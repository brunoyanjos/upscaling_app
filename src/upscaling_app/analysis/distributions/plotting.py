from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.plotting.colors import (
    get_gray,
    get_base_color,
)


def save_cdf_comparison(
    diameter: np.ndarray,
    experimental_cdf: np.ndarray,
    rr_cdf: np.ndarray,
    output: Path,
    *,
    experimental_color: str,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(
        diameter * 1e3,
        experimental_cdf,
        color=experimental_color,
        linewidth=2.0,
        marker="o",
        markersize=3,
        label="Experimental",
    )

    ax.plot(
        diameter * 1e3,
        rr_cdf,
        color=get_gray("regression"),
        linewidth=2.0,
        linestyle="--",
        label="Rosin-Rammler",
    )

    ax.set_xlabel("Droplet diameter [mm]")

    ax.set_ylabel("Cumulative volume fraction [-]")

    ax.set_ylim(
        0.0,
        1.0,
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


def save_pdf_comparison(
    edges: np.ndarray,
    experimental_density: np.ndarray,
    rr_diameter: np.ndarray,
    cdf_fit_density: np.ndarray,
    moment_fit_density: np.ndarray,
    output: Path,
    *,
    experimental_color: str,
) -> None:
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
        linewidth=2.0,
        label="Experimental",
    )

    ax.plot(
        rr_diameter * 1e3,
        cdf_fit_density / 1e3,
        color=get_gray("regression"),
        linewidth=2.0,
        linestyle="--",
        label="RR — direct CDF fit",
    )

    ax.plot(
        rr_diameter * 1e3,
        moment_fit_density / 1e3,
        color=get_gray("dark"),
        linewidth=1.8,
        linestyle=":",
        label="RR — discrete moments",
    )

    ax.set_xlabel("Droplet diameter [mm]")

    ax.set_ylabel("Volume density [mm⁻¹]")

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


def save_method_win_fraction_plot(
    comparison_summary: pd.DataFrame,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metric_labels = {
        "cdf_rmse": "CDF RMSE",
        "cdf_max_error": "CDF max error",
        "mass_rmse": "Bin-mass RMSE",
        "mass_max_error": "Bin-mass max error",
        "total_variation": "Total variation",
    }

    metric_order = list(metric_labels)

    data = comparison_summary.set_index("metric").loc[metric_order].reset_index()

    x = np.arange(len(data))

    width = 0.38

    fig, ax = plt.subplots(
        figsize=(10, 6),
    )

    ax.bar(
        x - width / 2,
        data["cdf_win_fraction"] * 100.0,
        width=width,
        color=get_gray("dark"),
        label="Direct CDF fit",
    )

    ax.bar(
        x + width / 2,
        data["moment_win_fraction"] * 100.0,
        width=width,
        color=get_gray("medium"),
        label="Discrete moments",
    )

    ax.set_xticks(x)

    ax.set_xticklabels(
        [metric_labels[metric] for metric in data["metric"]],
        rotation=20,
        ha="right",
    )

    ax.set_ylabel("Experiments won [%]")

    ax.set_ylim(
        0.0,
        105.0,
    )

    ax.grid(
        axis="y",
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


def save_method_improvement_by_regime_plot(
    comparison_by_regime: pd.DataFrame,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metric_labels = {
        "cdf_rmse": "CDF RMSE",
        "cdf_max_error": "CDF max error",
        "mass_rmse": "Bin-mass RMSE",
        "mass_max_error": "Bin-mass max error",
        "total_variation": "Total variation",
    }

    metric_order = list(metric_labels)

    regime_order = [
        "Untreated",
        "SSDI — Corexit",
        "SSDI — Finasol",
        "SSMD",
    ]

    regime_colors = {
        "Untreated": get_base_color("untreated"),
        "SSDI — Corexit": get_base_color("ssdi_corexit"),
        "SSDI — Finasol": get_base_color("ssdi_finasol"),
        "SSMD": get_base_color("ssmd"),
    }

    y = np.arange(len(metric_order))

    bar_height = 0.18

    fig, ax = plt.subplots(
        figsize=(10, 7),
    )

    for index, regime in enumerate(regime_order):
        subset = (
            comparison_by_regime.loc[comparison_by_regime["regime"] == regime]
            .set_index("metric")
            .loc[metric_order]
        )

        offset = (index - (len(regime_order) - 1) / 2) * bar_height

        ax.barh(
            y + offset,
            subset["mean_improvement_pct"].to_numpy(dtype=float),
            height=bar_height,
            color=regime_colors[regime],
            label=regime,
        )

    ax.axvline(
        0.0,
        color=get_gray("identity"),
        linewidth=1.5,
    )

    ax.set_yticks(y)

    ax.set_yticklabels([metric_labels[metric] for metric in metric_order])

    ax.set_xlabel("Mean error reduction relative to discrete moments [%]")

    ax.grid(
        axis="x",
        color=get_gray("grid"),
        alpha=0.8,
    )

    ax.legend()

    ax.invert_yaxis()

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)
