from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from upscaling_app.plotting.colors import (
    get_gray,
)
from upscaling_app.plotting.style import (
    apply_plot_style,
)


def save_model_comparison_plot(
    comparison: pd.DataFrame,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    apply_plot_style()

    data = comparison.copy()

    y = range(len(data))

    fig, ax = plt.subplots(
        figsize=(9, 6),
    )

    bars = ax.barh(
        y,
        data["log_mse"],
        color=get_gray("dark"),
        alpha=0.85,
    )

    ax.set_yticks(
        list(y),
        data["model"],
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
