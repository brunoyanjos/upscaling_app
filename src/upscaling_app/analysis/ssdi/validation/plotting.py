from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from upscaling_app.plotting.colors import (
    get_gray,
)
from upscaling_app.plotting.style import (
    apply_plot_style,
)


def _save_oil_metric_plot(
    *,
    folds: pd.DataFrame,
    column: str,
    ylabel: str,
    output: Path,
    zero_line: bool = False,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = folds.sort_values("held_out_oil")

    apply_plot_style()

    fig, ax = plt.subplots(
        figsize=(9, 6),
    )

    ax.bar(
        data["held_out_oil"].astype(str),
        data[column],
        color=get_gray("dark"),
        alpha=0.85,
    )

    if zero_line:
        ax.axhline(
            0.0,
            color=get_gray("identity"),
            linestyle="--",
            linewidth=1.5,
        )

    ax.set_xlabel("Held-out oil")

    ax.set_ylabel(ylabel)

    ax.grid(
        axis="y",
        linestyle="--",
        color=get_gray("grid"),
        alpha=0.7,
    )

    ax.set_axisbelow(True)

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_loo_log_mse_plot(
    folds: pd.DataFrame,
    output: Path,
) -> None:
    _save_oil_metric_plot(
        folds=folds,
        column="test_log_mse",
        ylabel="Held-out Log-MSE",
        output=output,
    )


def save_loo_mape_plot(
    folds: pd.DataFrame,
    output: Path,
) -> None:
    _save_oil_metric_plot(
        folds=folds,
        column="test_mape",
        ylabel="Held-out MAPE [%]",
        output=output,
    )


def save_loo_bias_plot(
    folds: pd.DataFrame,
    output: Path,
) -> None:
    _save_oil_metric_plot(
        folds=folds,
        column="mean_log_residual",
        ylabel="Mean logarithmic residual",
        output=output,
        zero_line=True,
    )


def save_validation_comparison_plot(
    comparison: pd.DataFrame,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    apply_plot_style()

    data = comparison.copy()

    fig, ax = plt.subplots(
        figsize=(9, 6),
    )

    bars = ax.barh(
        data["validation"],
        data["log_mse"],
        color=get_gray("dark"),
        alpha=0.85,
    )

    ax.invert_yaxis()

    ax.set_xlabel("Log-MSE")

    for bar, (_, row) in zip(
        bars,
        data.iterrows(),
    ):
        ax.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            (f"  {row['log_mse']:.3f}" f"  (n={int(row['n'])})"),
            va="center",
        )

    ax.grid(
        axis="x",
        linestyle="--",
        color=get_gray("grid"),
        alpha=0.7,
    )

    ax.set_axisbelow(True)

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)
