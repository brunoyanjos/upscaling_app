from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.plotting.colors import (
    get_base_color,
    get_gray,
)
from upscaling_app.plotting.style import (
    apply_plot_style,
)


def _require_columns(
    data: pd.DataFrame,
    columns: list[str],
    *,
    source: str,
) -> None:
    missing = [column for column in columns if column not in data.columns]

    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def save_loo_parity_plot(
    predictions: pd.DataFrame,
    output: Path,
) -> None:
    _require_columns(
        predictions,
        [
            "dR_exp",
            "dR_pred",
        ],
        source="SSMD LOO predictions",
    )

    observed = predictions["dR_exp"].to_numpy(
        dtype=float,
    )

    predicted = predictions["dR_pred"].to_numpy(
        dtype=float,
    )

    invalid = (
        ~np.isfinite(observed)
        | ~np.isfinite(predicted)
        | (observed <= 0.0)
        | (predicted <= 0.0)
    )

    if invalid.any():
        raise ValueError("SSMD LOO parity plot requires finite positive values.")

    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lower = float(
        min(
            observed.min(),
            predicted.min(),
        )
    )

    upper = float(
        max(
            observed.max(),
            predicted.max(),
        )
    )

    span = upper - lower
    margin = 0.05 * span if span > 0.0 else 0.05 * upper

    lower_limit = max(
        0.0,
        lower - margin,
    )

    upper_limit = upper + margin

    fig, ax = plt.subplots(
        figsize=(7, 7),
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
        linestyle="--",
        linewidth=1.5,
        color=get_gray("identity"),
        label="Identity",
        zorder=1,
    )

    ax.scatter(
        observed,
        predicted,
        s=45,
        color=get_base_color("ssmd"),
        edgecolor="white",
        linewidth=0.6,
        alpha=0.85,
        label="LOO prediction",
        zorder=2,
    )

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

    ax.set_xlabel(r"Measured $d_R$")

    ax.set_ylabel(r"Predicted $d_R$")

    ax.grid(
        alpha=0.35,
    )

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_loo_residual_by_oil_plot(
    by_oil: pd.DataFrame,
    output: Path,
) -> None:
    _require_columns(
        by_oil,
        [
            "oil_id",
            "mean_log_residual",
            "std_log_residual",
        ],
        source="SSMD LOO oil summary",
    )

    data = by_oil.sort_values("oil_id").reset_index(
        drop=True,
    )

    mean_residual = data["mean_log_residual"].to_numpy(
        dtype=float,
    )

    std_residual = data["std_log_residual"].to_numpy(
        dtype=float,
    )

    invalid = (
        ~np.isfinite(mean_residual) | ~np.isfinite(std_residual) | (std_residual < 0.0)
    )

    if invalid.any():
        raise ValueError("SSMD LOO residual plot contains invalid values.")

    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    x = np.arange(len(data))

    fig, ax = plt.subplots(
        figsize=(9, 6),
    )

    ax.axhline(
        0.0,
        linestyle="--",
        linewidth=1.3,
        color=get_gray("identity"),
        zorder=1,
    )

    ax.errorbar(
        x,
        mean_residual,
        yerr=std_residual,
        fmt="o",
        markersize=7,
        capsize=4,
        linewidth=1.5,
        color=get_base_color("ssmd"),
        ecolor=get_gray("medium"),
        label=r"Mean $\pm$ SD",
        zorder=2,
    )

    ax.set_xticks(x)

    ax.set_xticklabels(data["oil_id"].astype(str))

    ax.set_xlabel("Held-out oil")

    ax.set_ylabel(r"Log residual, $\ln(d_{R,\mathrm{exp}} / d_{R,\mathrm{pred}})$")

    ax.grid(
        axis="y",
        alpha=0.35,
    )

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(fig)
