from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.plotting.colors import (
    get_base_color,
    get_gray,
)

REGIME_ORDER = [
    "Untreated",
    "SSDI — Corexit",
    "SSDI — Finasol",
    "SSMD",
]


REGIME_COLORS = {
    "Untreated": get_base_color("untreated"),
    "SSDI — Corexit": get_base_color("ssdi_corexit"),
    "SSDI — Finasol": get_base_color("ssdi_finasol"),
    "SSMD": get_base_color("ssmd"),
}


def save_shape_by_regime_plot(
    data: pd.DataFrame,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    values = [
        data.loc[
            data["distribution_regime"] == regime,
            "shape",
        ].to_numpy(dtype=float)
        for regime in REGIME_ORDER
    ]

    fig, ax = plt.subplots(
        figsize=(9, 6),
    )

    boxplot = ax.boxplot(
        values,
        tick_labels=REGIME_ORDER,
        patch_artist=True,
        showfliers=False,
        medianprops={
            "color": "black",
            "linewidth": 1.6,
        },
    )

    for patch, regime in zip(
        boxplot["boxes"],
        REGIME_ORDER,
    ):
        patch.set_facecolor(REGIME_COLORS[regime])

        patch.set_alpha(0.35)

    rng = np.random.default_rng(42)

    for index, regime in enumerate(
        REGIME_ORDER,
        start=1,
    ):
        subset = data.loc[data["distribution_regime"] == regime]

        jitter = rng.normal(
            loc=0.0,
            scale=0.045,
            size=len(subset),
        )

        ax.scatter(
            index + jitter,
            subset["shape"],
            color=REGIME_COLORS[regime],
            s=28,
            alpha=0.75,
        )

    ax.set_ylabel("Rosin–Rammler shape parameter, k")

    ax.grid(
        axis="y",
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


def save_shape_vs_fit_quality_plot(
    data: pd.DataFrame,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    for regime in REGIME_ORDER:
        subset = data.loc[data["distribution_regime"] == regime]

        ax.scatter(
            subset["shape"],
            subset["cdf_total_variation"],
            color=REGIME_COLORS[regime],
            s=36,
            alpha=0.75,
            label=regime,
        )

    ax.set_xlabel("Rosin–Rammler shape parameter, k")

    ax.set_ylabel("Total variation")

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


def save_scale_by_regime_plot(
    data: pd.DataFrame,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    values = [
        (
            data.loc[
                data["distribution_regime"] == regime,
                "scale",
            ].to_numpy(dtype=float)
            * 1e3
        )
        for regime in REGIME_ORDER
    ]

    fig, ax = plt.subplots(
        figsize=(9, 6),
    )

    boxplot = ax.boxplot(
        values,
        tick_labels=REGIME_ORDER,
        patch_artist=True,
        showfliers=False,
        medianprops={
            "color": "black",
            "linewidth": 1.6,
        },
    )

    for patch, regime in zip(
        boxplot["boxes"],
        REGIME_ORDER,
    ):
        patch.set_facecolor(REGIME_COLORS[regime])
        patch.set_alpha(0.35)

    rng = np.random.default_rng(42)

    for index, regime in enumerate(
        REGIME_ORDER,
        start=1,
    ):
        subset = data.loc[data["distribution_regime"] == regime]

        jitter = rng.normal(
            loc=0.0,
            scale=0.045,
            size=len(subset),
        )

        ax.scatter(
            index + jitter,
            subset["scale"] * 1e3,
            color=REGIME_COLORS[regime],
            s=28,
            alpha=0.75,
        )

    ax.set_ylabel("Rosin–Rammler scale parameter, λ [mm]")

    ax.grid(
        axis="y",
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


def save_shape_vs_rr_d50_plot(
    data: pd.DataFrame,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    for regime in REGIME_ORDER:
        subset = data.loc[data["distribution_regime"] == regime]

        ax.scatter(
            subset["rr_d50"] * 1e3,
            subset["shape"],
            color=REGIME_COLORS[regime],
            s=36,
            alpha=0.75,
            label=regime,
        )

    ax.set_xlabel("Rosin–Rammler $D_{50}$ [mm]")

    ax.set_ylabel("Rosin–Rammler shape parameter, k")

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
