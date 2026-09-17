import matplotlib.pyplot as plt
import pandas as pd

from upscaling_app import paths
from upscaling_app.plotting.style import (
    APPLE_COLORS,
    APPLE_GRAYS,
    apply_plot_style,
)


def save_parity_plot(
    results: pd.DataFrame,
    metrics: dict[str, float],
    model_version: str,
) -> None:
    paths.FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    valid = results.loc[~results["is_outlier"]]
    outliers = results.loc[results["is_outlier"]]

    min_value = min(
        results["d50_exp"].min(),
        results["d50_pred"].min(),
    )

    max_value = max(
        results["d50_exp"].max(),
        results["d50_pred"].max(),
    )

    lower_limit = min_value * 0.8
    upper_limit = max_value * 1.2

    apply_plot_style()

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.scatter(
        valid["d50_exp"],
        valid["d50_pred"],
        color=APPLE_COLORS["blue"],
        label="Valid",
        alpha=0.75,
    )

    ax.scatter(
        outliers["d50_exp"],
        outliers["d50_pred"],
        color=APPLE_COLORS["red"],
        label="Outlier",
        alpha=0.9,
    )

    ax.plot(
        [lower_limit, upper_limit],
        [lower_limit, upper_limit],
        color=APPLE_GRAYS["gray"],
        linestyle="--",
        label="$y=x$",
    )

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlim(
        lower_limit,
        upper_limit,
    )

    ax.set_ylim(
        lower_limit,
        upper_limit,
    )

    ax.set_aspect("equal", adjustable="box")

    metric_text = (
        f"R² = {metrics['r2']:.4f}\n"
        f"RMSE = {metrics['rmse']:.2e} m\n"
        f"MAPE = {metrics['mape']:.2f}%"
    )

    ax.text(
        0.05,
        0.95,
        metric_text,
        transform=ax.transAxes,
        verticalalignment="top",
    )

    ax.set_xlabel("Experimental $d_{50}$ [m]")
    ax.set_ylabel("Predicted $d_{50}$ [m]")

    ax.legend()
    ax.grid(
        True,
        which="both",
        linestyle="--",
        alpha=0.3,
    )

    fig.tight_layout()

    output_path = paths.FIGURES_DIR / f"ssdi_parity_{model_version}.png"

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_leave_one_oil_out_plot(
    results: pd.DataFrame,
) -> None:
    apply_plot_style()

    paths.FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(8, 8),
    )

    oil_labels = results["held_out_oil"].astype(str)

    ax.bar(
        oil_labels,
        results["test_log_mse"],
        color=APPLE_COLORS["blue"],
    )

    ax.set_xlabel("Held-out oil")
    ax.set_ylabel("Test Log-MSE")

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4,
    )

    fig.tight_layout()

    output_path = paths.FIGURES_DIR / "ssdi_leave_one_oil_out_log_mse.png"

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_leave_one_oil_out_mape_plot(
    results: pd.DataFrame,
) -> None:
    apply_plot_style()

    paths.FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(8, 8),
    )

    oil_labels = results["held_out_oil"].astype(str)

    ax.bar(
        oil_labels,
        results["mape"],
        color=APPLE_COLORS["blue"],
    )

    ax.set_xlabel("Held-out oil")
    ax.set_ylabel("MAPE (%)")

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4,
    )

    fig.tight_layout()

    output_path = paths.FIGURES_DIR / "ssdi_leave_one_oil_out_mape.png"

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_leave_one_oil_out_bias_plot(
    results: pd.DataFrame,
) -> None:
    apply_plot_style()

    paths.FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(8, 8),
    )

    oil_labels = results["held_out_oil"].astype(str)

    ax.bar(
        oil_labels,
        results["mean_log_residual"],
        color=APPLE_COLORS["blue"],
    )

    ax.axhline(
        0.0,
        linewidth=1.0,
        color="black",
    )

    ax.set_xlabel("Held-out oil")
    ax.set_ylabel("Mean log residual")

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4,
    )

    fig.tight_layout()

    output_path = paths.FIGURES_DIR / "ssdi_leave_one_oil_out_bias.png"

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)
