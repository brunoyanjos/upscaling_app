from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from upscaling_app.plotting.colors import (
    get_base_color,
    get_gray,
)
from upscaling_app.plotting.style import apply_plot_style

REGIME_COLORS = {
    "Untreated": get_base_color("untreated"),
    "SSDI": get_base_color("corexit"),
    "SSMD": get_base_color("ssmd"),
}


def _format_regime_label(
    row: pd.Series,
) -> str:
    diameter_mm = row["nozzle_diameter"] * 1e3
    gas = "gas" if row["has_gas"] else "no gas"

    return f"{row['dispersion_kind']} — " f"{diameter_mm:g} mm — " f"{gas}"


def save_regime_coverage_plot(
    summary: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = summary.copy()

    data["label"] = data.apply(
        _format_regime_label,
        axis=1,
    )

    colors = [REGIME_COLORS[kind] for kind in data["dispersion_kind"]]

    y = np.arange(len(data))

    fig, ax = plt.subplots(
        figsize=(8, 5),
    )

    ax.barh(
        y,
        data["n_experiments"],
        color=colors,
    )

    ax.set_yticks(y)
    ax.set_yticklabels(data["label"])

    ax.set_xlabel("Number of experiments")
    ax.set_ylabel("")

    ax.invert_yaxis()

    ax.grid(
        axis="x",
        alpha=0.4,
    )
    ax.set_axisbelow(True)

    fig.tight_layout()

    fig.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_oil_treatment_coverage_plot(
    coverage: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = coverage.set_index("oil_id")

    values = data.to_numpy(dtype=float)

    cmap = LinearSegmentedColormap.from_list(
        "coverage",
        [
            get_gray("background"),
            get_gray("dark"),
        ],
    )

    fig, ax = plt.subplots(
        figsize=(9, 6),
    )

    image = ax.imshow(
        values,
        aspect="auto",
        cmap=cmap,
    )

    ax.set_xticks(np.arange(len(data.columns)))
    ax.set_xticklabels(
        data.columns,
        rotation=45,
        ha="right",
    )

    ax.set_yticks(np.arange(len(data.index)))
    ax.set_yticklabels(
        data.index,
    )

    ax.set_xlabel("Treatment")
    ax.set_ylabel("Oil")

    max_value = values.max() if values.size else 0.0

    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            value = values[i, j]

            text_color = (
                "white"
                if max_value > 0 and value > 0.5 * max_value
                else get_gray("text")
            )

            ax.text(
                j,
                i,
                f"{value:g}",
                ha="center",
                va="center",
                color=text_color,
            )

    colorbar = fig.colorbar(
        image,
        ax=ax,
        pad=0.02,
    )
    colorbar.set_label("Number of experiments")

    fig.tight_layout()

    fig.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(fig)
