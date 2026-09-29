from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from upscaling_app.plotting.colors import (
    get_base_color,
    get_gray,
)
from upscaling_app.plotting.style import (
    apply_plot_style,
)

NOZZLE_MARKERS = {
    0.002: "o",
    0.003: "s",
}


def _dispersion_regime(
    dispersion_tag: str,
) -> str:
    tag = str(dispersion_tag).lower()

    if "untreated" in tag:
        return "untreated"

    if "c9500" in tag:
        return "c9500"

    if "ibc" in tag:
        return "ibc"

    raise ValueError(f"Unknown SSDI dispersion tag: {dispersion_tag!r}")


def save_sensitivity_parity_plot(
    results: pd.DataFrame,
    metrics: dict[str, float],
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = results.copy()

    data["dispersion_regime"] = data["dispersion_tag"].map(_dispersion_regime)

    min_value = min(
        data["d50_exp"].min(),
        data["d50_pred"].min(),
    )

    max_value = max(
        data["d50_exp"].max(),
        data["d50_pred"].max(),
    )

    lower_limit = min_value * 0.8
    upper_limit = max_value * 1.2

    apply_plot_style()

    fig, ax = plt.subplots(
        figsize=(8, 8),
    )

    regime_labels = {
        "untreated": "Untreated",
        "c9500": "C9500",
        "ibc": "IBC",
    }

    regime_order = (
        "untreated",
        "c9500",
        "ibc",
    )

    nozzle_order = (
        0.002,
        0.003,
    )

    for nozzle_diameter in nozzle_order:
        for regime in regime_order:
            group = data.loc[
                (data["dispersion_regime"] == regime)
                & (data["nozzle_diameter"] == nozzle_diameter)
            ]

            if group.empty:
                continue

            color = get_base_color(regime)

            marker = NOZZLE_MARKERS[nozzle_diameter]

            diameter_mm = nozzle_diameter * 1e3

            label = f"{regime_labels[regime]}" f" — {diameter_mm:g} mm"

            ax.scatter(
                group["d50_exp"],
                group["d50_pred"],
                color=color,
                marker=marker,
                s=52,
                alpha=0.88,
                edgecolors=get_gray("dark"),
                linewidths=0.35,
                label=label,
                zorder=2,
            )

    ax.plot(
        [
            lower_limit,
            upper_limit,
        ],
        [
            lower_limit,
            upper_limit,
        ],
        color=get_gray("identity"),
        linestyle="--",
        linewidth=1.6,
        label="$y=x$",
        zorder=1,
    )

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlim(
        lower_limit,
        upper_limit,
    )

    ax.set_ylim(
        lower_limit,
        upper_limit,
    )

    ax.set_aspect(
        "equal",
        adjustable="box",
    )

    metric_text = (
        f"Log-MSE = {metrics['log_mse']:.4f}\n"
        f"$R^2$ = {metrics['r2']:.4f}\n"
        f"RMSE = {metrics['rmse'] * 1e3:.3f} mm\n"
        f"MAPE = {metrics['mape']:.1f}%"
    )

    ax.text(
        0.05,
        0.95,
        metric_text,
        transform=ax.transAxes,
        verticalalignment="top",
    )

    ax.set_xlabel("Experimental $d_{50}$ [m]")

    ax.set_ylabel("Predicted $d_{50}$ [m]")

    ax.legend(
        loc="lower right",
        frameon=False,
    )

    ax.grid(
        True,
        which="both",
        linestyle="--",
        color=get_gray("grid"),
        alpha=0.65,
    )

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)
