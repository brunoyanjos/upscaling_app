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


def _get_identity_limits(
    x: np.ndarray,
    y: np.ndarray,
) -> tuple[float, float]:
    values = np.concatenate(
        [
            np.asarray(x, dtype=float),
            np.asarray(y, dtype=float),
        ]
    )

    values = values[np.isfinite(values)]

    if values.size == 0:
        raise ValueError("No finite values available for parity plot.")

    minimum = float(np.min(values))

    maximum = float(np.max(values))

    span = maximum - minimum

    padding = 0.05 * span if span > 0.0 else 0.1

    lower = max(
        0.0,
        minimum - padding,
    )

    upper = maximum + padding

    return lower, upper


def save_shape_scale_parity_plot(
    pairs: pd.DataFrame,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lower, upper = _get_identity_limits(
        pairs["shape_2mm"].to_numpy(dtype=float),
        pairs["shape_3mm"].to_numpy(dtype=float),
    )

    fig, ax = plt.subplots(
        figsize=(7, 7),
    )

    for regime in REGIME_ORDER:
        subset = pairs.loc[pairs["distribution_regime"] == regime]

        if subset.empty:
            continue

        ax.scatter(
            subset["shape_2mm"],
            subset["shape_3mm"],
            color=REGIME_COLORS[regime],
            s=45,
            alpha=0.8,
            label=regime,
        )

    ax.plot(
        [lower, upper],
        [lower, upper],
        linestyle="--",
        color=get_gray("dark"),
        linewidth=1.5,
        label="Identity",
    )

    ax.set_xlim(
        lower,
        upper,
    )

    ax.set_ylim(
        lower,
        upper,
    )

    ax.set_aspect(
        "equal",
        adjustable="box",
    )

    ax.set_xlabel(r"$k$ — 2 mm, no gas")

    ax.set_ylabel(r"$k$ — 3 mm, no gas")

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


def save_shape_gas_parity_plot(
    pairs: pd.DataFrame,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lower, upper = _get_identity_limits(
        pairs["shape_no_gas"].to_numpy(dtype=float),
        pairs["shape_gas"].to_numpy(dtype=float),
    )

    fig, ax = plt.subplots(
        figsize=(7, 7),
    )

    for regime in REGIME_ORDER:
        subset = pairs.loc[pairs["distribution_regime"] == regime]

        if subset.empty:
            continue

        ax.scatter(
            subset["shape_no_gas"],
            subset["shape_gas"],
            color=REGIME_COLORS[regime],
            s=45,
            alpha=0.8,
            label=regime,
        )

    ax.plot(
        [lower, upper],
        [lower, upper],
        linestyle="--",
        color=get_gray("dark"),
        linewidth=1.5,
        label="Identity",
    )

    ax.set_xlim(
        lower,
        upper,
    )

    ax.set_ylim(
        lower,
        upper,
    )

    ax.set_aspect(
        "equal",
        adjustable="box",
    )

    ax.set_xlabel(r"$k$ — 2 mm, no gas")

    ax.set_ylabel(r"$k$ — 2 mm, gas")

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
