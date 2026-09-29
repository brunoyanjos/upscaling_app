from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.plotting.colors import (
    get_gray,
)
from upscaling_app.plotting.style import (
    apply_plot_style,
)


def save_oil_wise_log_mse_plot(
    by_oil: pd.DataFrame,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    apply_plot_style()

    data = by_oil.sort_values(
        "oil_id",
    )

    x = np.arange(len(data))

    width = 0.36

    fig, ax = plt.subplots(
        figsize=(10, 6),
    )

    ax.bar(
        x - width / 2,
        data["log_mse_global"],
        width,
        label="Global calibration",
        color=get_gray("medium"),
    )

    ax.bar(
        x + width / 2,
        data["log_mse_oil_wise"],
        width,
        label="Oil-wise calibration",
        color=get_gray("dark"),
    )

    ax.set_xticks(
        x,
        data["oil_id"].astype(str),
    )

    ax.set_xlabel("Oil")

    ax.set_ylabel("Log-MSE")

    ax.legend(
        frameon=False,
    )

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
