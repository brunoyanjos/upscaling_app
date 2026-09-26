from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.plotting.colors import (
    GRAY_COLORS,
    SCIENTIFIC_COLORS,
)
from upscaling_app.plotting.style import apply_plot_style

REGIME_ORDER = (
    "3 mm — no gas",
    "2 mm — no gas",
    "2 mm — gas",
)


REGIME_COLORS = {
    "3 mm — no gas": SCIENTIFIC_COLORS["ssmd"][300],
    "2 mm — no gas": SCIENTIFIC_COLORS["ssmd"][500],
    "2 mm — gas": SCIENTIFIC_COLORS["ssmd"][700],
}


def save_ssmd_regime_response_plot(
    summary: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(9, 7),
    )

    for regime in REGIME_ORDER:
        group = summary.loc[summary["regime"] == regime].sort_values(
            "water_jet_fraction"
        )

        if group.empty:
            continue

        color = REGIME_COLORS[regime]

        ax.plot(
            group["water_jet_pct"],
            group["median_reduction_pct"],
            marker="o",
            color=color,
            linewidth=2.2,
            label=regime,
            zorder=3,
        )

        ax.fill_between(
            group["water_jet_pct"],
            group["q1_reduction_pct"],
            group["q3_reduction_pct"],
            color=color,
            alpha=0.15,
            linewidth=0.0,
            zorder=1,
        )

    ax.set_xlabel("Water-jet fraction [%]")
    ax.set_ylabel(r"Median $d_{50}$ reduction [%]")

    water_jet_levels = sorted(summary["water_jet_pct"].dropna().unique())

    ax.set_xticks(
        water_jet_levels,
    )

    ax.grid(
        axis="y",
        alpha=0.3,
    )
    ax.set_axisbelow(True)

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_ssmd_gas_effect_plot(
    summary: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = summary.sort_values("water_jet_fraction")

    x = data["water_jet_pct"]
    y = data["median_dR_gas_to_no_gas"]

    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    ax.plot(
        x,
        y,
        marker="o",
        color=SCIENTIFIC_COLORS["ssmd"][700],
        linewidth=2.2,
        zorder=3,
    )

    ax.fill_between(
        x,
        data["q1_dR_gas_to_no_gas"],
        data["q3_dR_gas_to_no_gas"],
        color=SCIENTIFIC_COLORS["ssmd"][700],
        alpha=0.15,
        linewidth=0.0,
        zorder=1,
    )

    ax.axhline(
        1.0,
        color=GRAY_COLORS["identity"],
        linestyle="--",
        linewidth=1.5,
        zorder=2,
    )

    ax.set_xlabel("Water-jet fraction [%]")
    ax.set_ylabel(r"Median $d_{R,\mathrm{gas}}" r"/d_{R,\mathrm{no\ gas}}$")

    ax.set_xticks(
        x,
    )

    ax.grid(
        axis="y",
        alpha=0.3,
    )
    ax.set_axisbelow(True)

    fig.tight_layout()

    fig.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_ssmd_momentum_response_plot(
    data: pd.DataFrame,
    relation_summary: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    valid = (
        data["momentum_amplification"].notna()
        & data["dR_measured"].notna()
        & np.isfinite(data["momentum_amplification"])
        & np.isfinite(data["dR_measured"])
        & (data["momentum_amplification"] > 0.0)
        & (data["dR_measured"] > 0.0)
    )

    plot_data = data.loc[valid].copy()

    if plot_data.empty:
        raise ValueError("No valid SSMD momentum-response data.")

    global_metrics = relation_summary.loc[relation_summary["regime"] == "global"]

    if len(global_metrics) != 1:
        raise ValueError("Expected exactly one global momentum relation.")

    global_metrics = global_metrics.iloc[0]

    fig, ax = plt.subplots(
        figsize=(9, 7),
    )

    for regime in REGIME_ORDER:
        group = plot_data.loc[plot_data["regime"] == regime]

        if group.empty:
            continue

        ax.scatter(
            group["momentum_amplification"],
            group["dR_measured"],
            color=REGIME_COLORS[regime],
            label=regime,
            alpha=0.70,
            zorder=3,
        )

    x_fit = np.logspace(
        np.log10(plot_data["momentum_amplification"].min()),
        np.log10(plot_data["momentum_amplification"].max()),
        200,
    )

    y_fit = 10.0 ** float(global_metrics["intercept"]) * x_fit ** float(
        global_metrics["slope"]
    )

    ax.plot(
        x_fit,
        y_fit,
        color=GRAY_COLORS["regression"],
        linestyle="--",
        linewidth=2.0,
        label="Global log-log fit",
        zorder=2,
    )

    ax.text(
        0.05,
        0.05,
        (
            f"Slope = "
            f"{global_metrics['slope']:.3f}\n"
            f"$R^2_{{\\log}}$ = "
            f"{global_metrics['r2_log']:.3f}"
        ),
        transform=ax.transAxes,
        va="bottom",
    )

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlabel(r"Momentum amplification, $A_M$")
    ax.set_ylabel(r"Relative droplet size, $d_R$")

    ax.grid(
        True,
        which="both",
        alpha=0.3,
    )
    ax.set_axisbelow(True)

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(fig)
