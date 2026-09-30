from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.plotting.colors import (
    get_base_color,
    get_gray,
)
from upscaling_app.plotting.style import apply_plot_style


def _require_columns(
    data: pd.DataFrame,
    columns: list[str],
    *,
    source: str,
) -> None:
    missing = [column for column in columns if column not in data.columns]

    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def _get_axis_limits(
    *arrays: np.ndarray,
) -> tuple[float, float]:
    values = np.concatenate([np.asarray(array, dtype=float) for array in arrays])

    valid = values[np.isfinite(values) & (values > 0.0)]

    if valid.size == 0:
        raise ValueError("Parity plot requires finite positive values.")

    lower = float(valid.min())
    upper = float(valid.max())

    if lower == upper:
        lower *= 0.8
        upper *= 1.2
    else:
        lower *= 0.8
        upper *= 1.2

    return lower, upper


def _plot_parity_panel(
    ax: plt.Axes,
    *,
    observed: np.ndarray,
    predicted: np.ndarray,
    title: str,
    limits: tuple[float, float],
) -> None:
    lower, upper = limits

    ax.scatter(
        observed,
        predicted,
        s=55,
        color=get_base_color("ssmd"),
        alpha=0.80,
        edgecolors="none",
    )

    ax.plot(
        [lower, upper],
        [lower, upper],
        linestyle="--",
        linewidth=1.5,
        color=get_gray("identity"),
        label="Identity",
    )

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlim(
        lower,
        upper,
    )

    ax.set_ylim(
        lower,
        upper,
    )

    ax.set_title(title)

    ax.set_box_aspect(1)


def _save_parity_comparison(
    *,
    reference: pd.DataFrame,
    global_model: pd.DataFrame,
    observed_column: str,
    predicted_column: str,
    xlabel: str,
    ylabel: str,
    output: Path,
    scale_factor: float = 1.0,
) -> None:
    _require_columns(
        reference,
        [
            observed_column,
            predicted_column,
        ],
        source="SINTEF reference predictions",
    )

    _require_columns(
        global_model,
        [
            observed_column,
            predicted_column,
        ],
        source="Global c,d predictions",
    )

    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    reference_observed = reference[observed_column].to_numpy(dtype=float) * scale_factor

    reference_predicted = (
        reference[predicted_column].to_numpy(dtype=float) * scale_factor
    )

    global_observed = global_model[observed_column].to_numpy(dtype=float) * scale_factor

    global_predicted = (
        global_model[predicted_column].to_numpy(dtype=float) * scale_factor
    )

    limits = _get_axis_limits(
        reference_observed,
        reference_predicted,
        global_observed,
        global_predicted,
    )

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(12, 6),
        sharex=True,
        sharey=True,
    )

    _plot_parity_panel(
        axes[0],
        observed=reference_observed,
        predicted=reference_predicted,
        title="SINTEF reference",
        limits=limits,
    )

    _plot_parity_panel(
        axes[1],
        observed=global_observed,
        predicted=global_predicted,
        title="Global c,d",
        limits=limits,
    )

    axes[0].set_xlabel(xlabel)

    axes[1].set_xlabel(xlabel)

    axes[0].set_ylabel(ylabel)

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_dR_parity_plot(
    *,
    reference: pd.DataFrame,
    global_model: pd.DataFrame,
    output: Path,
) -> None:
    _save_parity_comparison(
        reference=reference,
        global_model=global_model,
        observed_column="dR_exp",
        predicted_column="dR_pred",
        xlabel=r"Experimental $d_R$",
        ylabel=r"Predicted $d_R$",
        output=output,
    )


def save_d50_parity_plot(
    *,
    reference: pd.DataFrame,
    global_model: pd.DataFrame,
    output: Path,
) -> None:
    _save_parity_comparison(
        reference=reference,
        global_model=global_model,
        observed_column="d50_exp",
        predicted_column="d50_pred",
        xlabel=r"Experimental $d_{50}$ [mm]",
        ylabel=r"Predicted $d_{50}$ [mm]",
        output=output,
        scale_factor=1e3,
    )
