from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from upscaling_app.plotting.colors import (
    GRAY_COLORS,
    get_base_color,
    get_ssmd_fraction_color,
)
from upscaling_app.plotting.style import apply_plot_style

TREATMENT_ORDER = (
    "SSDI-C9500",
    "SSDI-IBC",
    "WJ-40%",
    "WJ-45%",
    "WJ-50%",
    "WJ-55%",
)


def _get_treatment_color(treatment: str) -> str:
    if treatment == "SSDI-C9500":
        return get_base_color("corexit")

    if treatment == "SSDI-IBC":
        return get_base_color("finasol")

    if treatment.startswith("WJ-"):
        fraction = float(treatment.removeprefix("WJ-").removesuffix("%")) / 100.0

        return get_ssmd_fraction_color(fraction)

    return GRAY_COLORS["medium"]


def save_treatment_reduction_plot(
    summary: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    treatments = [
        treatment
        for treatment in TREATMENT_ORDER
        if treatment in summary["dispersion_tag"].values
    ]

    data = summary.set_index("dispersion_tag").loc[treatments].reset_index()

    colors = [_get_treatment_color(treatment) for treatment in data["dispersion_tag"]]

    x = np.arange(len(data))

    fig, ax = plt.subplots(
        figsize=(9, 6),
    )

    bars = ax.bar(
        x,
        data["median_reduction_pct"],
        color=colors,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(
        data["dispersion_tag"],
        rotation=30,
        ha="right",
    )

    ax.set_ylabel(r"Median $d_{50}$ reduction [%]")
    ax.set_xlabel("")

    ax.grid(
        axis="y",
        alpha=0.4,
    )
    ax.set_axisbelow(True)

    for bar, value in zip(
        bars,
        data["median_reduction_pct"],
    ):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 1.0,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
        )

    fig.tight_layout()

    fig.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_treatment_by_oil_plot(
    by_oil: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = by_oil.pivot(
        index="oil_id",
        columns="dispersion_tag",
        values="median_reduction_pct",
    )

    treatments = [
        treatment for treatment in TREATMENT_ORDER if treatment in data.columns
    ]

    data = data.reindex(
        columns=treatments,
    )

    values = data.to_numpy(dtype=float)

    cmap = LinearSegmentedColormap.from_list(
        "treatment_effect",
        [
            GRAY_COLORS["background"],
            GRAY_COLORS["dark"],
        ],
    )

    fig, ax = plt.subplots(
        figsize=(9, 6),
    )

    image = ax.imshow(
        values,
        aspect="auto",
        cmap=cmap,
        vmin=0.0,
        vmax=100.0,
    )

    ax.set_xticks(np.arange(len(data.columns)))
    ax.set_xticklabels(
        data.columns,
        rotation=30,
        ha="right",
    )

    ax.set_yticks(np.arange(len(data.index)))
    ax.set_yticklabels(
        data.index.astype(str),
    )

    ax.set_xlabel("Treatment")
    ax.set_ylabel("Oil")

    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            value = values[i, j]

            if np.isnan(value):
                continue

            text_color = "white" if value >= 60.0 else GRAY_COLORS["text"]

            ax.text(
                j,
                i,
                f"{value:.1f}",
                ha="center",
                va="center",
                color=text_color,
                fontsize=10,
            )

    colorbar = fig.colorbar(
        image,
        ax=ax,
        pad=0.02,
    )
    colorbar.set_label(r"$d_{50}$ reduction [%]")

    fig.tight_layout()

    fig.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(fig)
