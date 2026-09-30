from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.plotting.colors import (
    get_base_color,
)
from upscaling_app.plotting.style import (
    apply_plot_style,
)


def _require_columns(
    data: pd.DataFrame,
    columns: list[str],
) -> None:
    missing = [column for column in columns if column not in data.columns]

    if missing:
        raise ValueError(f"SSMD oil-wise plotting data is missing columns: {missing}")


def _prepare_data(
    comparison: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        comparison,
        [
            "oil_id",
            "k_global",
            "k_global_std",
            "k_oil",
            "k_oil_std",
            "k_global_cv_pct",
            "k_oil_cv_pct",
        ],
    )

    return comparison.sort_values("oil_id").reset_index(
        drop=True,
    )


def save_factor_comparison_plot(
    *,
    comparison: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = _prepare_data(
        comparison,
    )

    x = np.arange(
        len(data),
    )

    offset = 0.10

    color = get_base_color("ssmd")

    fig, ax = plt.subplots(
        figsize=(10, 6),
    )

    for index, row in data.iterrows():
        ax.plot(
            [x[index], x[index]],
            [
                row["k_global"],
                row["k_oil"],
            ],
            linewidth=1.0,
            color=color,
            alpha=0.25,
        )

    ax.errorbar(
        x - offset,
        data["k_global"],
        yerr=data["k_global_std"],
        fmt="o",
        markersize=7,
        capsize=4,
        linewidth=1.4,
        color=color,
        alpha=0.45,
        label="Global $c,d$",
    )

    ax.errorbar(
        x + offset,
        data["k_oil"],
        yerr=data["k_oil_std"],
        fmt="s",
        markersize=7,
        capsize=4,
        linewidth=1.4,
        color=color,
        alpha=0.95,
        label="Oil-wise factor",
    )

    ax.set_xticks(
        x,
        data["oil_id"].astype(str),
    )

    ax.set_xlabel("Oil ID")

    ax.set_ylabel(r"Property factor $k$")

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_factor_variability_plot(
    *,
    comparison: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = _prepare_data(
        comparison,
    )

    x = np.arange(
        len(data),
    )

    width = 0.36

    color = get_base_color("ssmd")

    fig, ax = plt.subplots(
        figsize=(10, 6),
    )

    ax.bar(
        x - width / 2,
        data["k_global_cv_pct"],
        width=width,
        color=color,
        alpha=0.35,
        label="Global $c,d$",
    )

    ax.bar(
        x + width / 2,
        data["k_oil_cv_pct"],
        width=width,
        color=color,
        alpha=0.90,
        label="Oil-wise factor",
    )

    ax.set_xticks(
        x,
        data["oil_id"].astype(str),
    )

    ax.set_xlabel("Oil ID")

    ax.set_ylabel("Coefficient of variation [%]")

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)
