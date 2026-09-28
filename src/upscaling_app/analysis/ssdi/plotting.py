import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from upscaling_app import paths
from upscaling_app.plotting.colors import (
    get_base_color,
    get_gray,
    get_regime_color,
)
from upscaling_app.plotting.style import (
    apply_plot_style,
)

MODEL_ORDER = [
    "reference",
    "global",
    "oil_wise",
]


MODEL_TITLES = {
    "reference": "SINTEF reference",
    "global": "Global calibration",
    "oil_wise": "Oil-wise calibration",
}

NOZZLE_MARKERS = {
    0.002: "o",
    0.003: "s",
}


# =========================================================
# Helpers
# =========================================================


def _dispersion_regime(
    dispersion_tag: str,
) -> str:
    tag = str(dispersion_tag).lower()

    if "untreated" in tag:
        return "untreated"

    if "c9500" in tag:
        return "c9500"

    if "ibc" in tag:
        return "ibc"

    raise ValueError(f"Unknown SSDI dispersion tag: {dispersion_tag!r}")


def _dispersion_label(
    dispersion_tag: str,
    nozzle_diameter: float,
) -> str:
    regime = _dispersion_regime(dispersion_tag)

    labels = {
        "untreated": "Untreated",
        "c9500": "C9500",
        "ibc": "IBC",
    }

    diameter_mm = float(nozzle_diameter) * 1e3

    return f"{labels[regime]} — " f"{diameter_mm:g} mm"


# =========================================================
# Standard parity plot
# =========================================================


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

    fig, ax = plt.subplots(
        figsize=(8, 8),
    )

    ax.scatter(
        valid["d50_exp"],
        valid["d50_pred"],
        color=get_gray("dark"),
        label="Valid",
        alpha=0.75,
    )

    ax.scatter(
        outliers["d50_exp"],
        outliers["d50_pred"],
        color=get_gray("medium"),
        label="Outlier",
        alpha=0.90,
    )

    ax.plot(
        [
            lower_limit,
            upper_limit,
        ],
        [
            lower_limit,
            upper_limit,
        ],
        color=get_gray("identity"),
        linestyle="--",
        linewidth=1.5,
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

    ax.set_aspect(
        "equal",
        adjustable="box",
    )

    metric_text = (
        f"$R^2$ = {metrics['r2']:.4f}\n"
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
        color=get_gray("grid"),
        alpha=0.65,
    )

    fig.tight_layout()

    output_path = paths.FIGURES_DIR / f"ssdi_parity_{model_version}.png"

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


# =========================================================
# Leave-one-oil-out plots
# =========================================================


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
        color=get_gray("regression"),
    )

    ax.set_xlabel("Held-out oil")

    ax.set_ylabel("Test Log-MSE")

    ax.grid(
        axis="y",
        linestyle="--",
        color=get_gray("grid"),
        alpha=0.7,
    )

    ax.set_axisbelow(True)

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
        color=get_gray("regression"),
    )

    ax.set_xlabel("Held-out oil")

    ax.set_ylabel("MAPE (%)")

    ax.grid(
        axis="y",
        linestyle="--",
        color=get_gray("grid"),
        alpha=0.7,
    )

    ax.set_axisbelow(True)

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
        color=get_gray("regression"),
    )

    ax.axhline(
        0.0,
        linewidth=1.2,
        color=get_gray("dark"),
    )

    ax.set_xlabel("Held-out oil")

    ax.set_ylabel("Mean log residual")

    ax.grid(
        axis="y",
        linestyle="--",
        color=get_gray("grid"),
        alpha=0.7,
    )

    ax.set_axisbelow(True)

    fig.tight_layout()

    output_path = paths.FIGURES_DIR / "ssdi_leave_one_oil_out_bias.png"

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


# =========================================================
# Presentation — model parity comparison
# =========================================================


def save_ssdi_model_parity_comparison(
    predictions: pd.DataFrame,
    overall: pd.DataFrame,
) -> None:
    apply_plot_style()

    paths.FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = predictions.copy()

    metrics = overall.set_index("model")

    # Presentation units only.
    data["d50_exp_mm"] = data["d50_exp"] * 1e3

    data["d50_pred_mm"] = data["d50_pred"] * 1e3

    min_value = min(
        data["d50_exp_mm"].min(),
        data["d50_pred_mm"].min(),
    )

    max_value = max(
        data["d50_exp_mm"].max(),
        data["d50_pred_mm"].max(),
    )

    lower_limit = min_value * 0.8

    upper_limit = max_value * 1.2

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(16, 5.8),
        sharex=True,
        sharey=True,
    )

    legend_handles = []
    legend_labels = []

    for ax, model in zip(
        axes,
        MODEL_ORDER,
    ):
        model_data = data.loc[data["model"] == model]

        groups = model_data.groupby(
            [
                "dispersion_tag",
                "nozzle_diameter",
            ],
            sort=False,
        )

        for (
            dispersion_tag,
            nozzle_diameter,
        ), group in groups:
            regime = _dispersion_regime(dispersion_tag)

            color = get_base_color(regime)

            marker = NOZZLE_MARKERS[float(nozzle_diameter)]

            label = _dispersion_label(
                dispersion_tag,
                nozzle_diameter,
            )

            scatter = ax.scatter(
                group["d50_exp_mm"],
                group["d50_pred_mm"],
                color=color,
                marker=marker,
                s=52,
                alpha=0.88,
                edgecolors=get_gray("dark"),
                linewidths=0.35,
                zorder=2,
            )

            if model == MODEL_ORDER[0] and label not in legend_labels:
                legend_handles.append(scatter)

                legend_labels.append(label)

        ax.plot(
            [
                lower_limit,
                upper_limit,
            ],
            [
                lower_limit,
                upper_limit,
            ],
            color=get_gray("identity"),
            linestyle="--",
            linewidth=1.6,
            zorder=1,
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

        ax.set_aspect(
            "equal",
            adjustable="box",
        )

        row = metrics.loc[model]

        metric_text = (
            f"$R^2$ = {row['r2']:.3f}\n"
            f"RMSE = {row['rmse'] * 1e3:.3f} mm\n"
            f"MAPE = {row['mape']:.1f}%"
        )

        ax.text(
            0.05,
            0.95,
            metric_text,
            transform=ax.transAxes,
            verticalalignment="top",
            horizontalalignment="left",
        )

        ax.set_title(MODEL_TITLES[model])

        ax.set_xlabel("Measured $d_{50}$ [mm]")

        ax.grid(
            True,
            which="both",
            linestyle="--",
            color=get_gray("grid"),
            alpha=0.65,
        )

        ax.set_axisbelow(True)

    axes[0].set_ylabel("Predicted $d_{50}$ [mm]")

    # Explicitly identify the local fit as in-sample.
    axes[2].text(
        0.95,
        0.05,
        "In-sample calibration",
        transform=axes[2].transAxes,
        horizontalalignment="right",
        verticalalignment="bottom",
        fontsize=10,
        color=get_gray("regression"),
    )

    fig.legend(
        legend_handles,
        legend_labels,
        loc="lower center",
        ncol=3,
        frameon=False,
    )

    fig.tight_layout(
        rect=[
            0.0,
            0.13,
            1.0,
            1.0,
        ]
    )

    output_path = paths.FIGURES_DIR / "ssdi_model_parity_comparison.png"

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


# =========================================================
# Presentation — gas / no-gas performance
# =========================================================


def save_ssdi_gas_performance_plot(
    by_gas: pd.DataFrame,
) -> None:
    apply_plot_style()

    paths.FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = by_gas.copy()

    pivot = data.pivot(
        index="model",
        columns="has_gas",
        values="log_mse",
    ).reindex(MODEL_ORDER)

    x = np.arange(len(MODEL_ORDER))

    width = 0.34

    fig, ax = plt.subplots(
        figsize=(9, 6),
    )

    no_gas_bars = ax.bar(
        x - width / 2,
        pivot[False],
        width,
        label="No gas",
        color=get_base_color("untreated"),
    )

    gas_bars = ax.bar(
        x + width / 2,
        pivot[True],
        width,
        label="Gas",
        color=get_base_color("ssmd"),
    )

    ax.bar_label(
        no_gas_bars,
        fmt="%.3f",
        padding=4,
        fontsize=10,
    )

    ax.bar_label(
        gas_bars,
        fmt="%.3f",
        padding=4,
        fontsize=10,
    )

    ax.set_xticks(
        x,
        [
            "SINTEF\nreference",
            "Global\ncalibration",
            "Oil-wise\ncalibration",
        ],
    )

    ax.set_ylabel("Log-MSE")

    ax.set_title("SSDI prediction performance — 2 mm nozzle")

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

    upper_limit = max(
        pivot[False].max(),
        pivot[True].max(),
    )

    ax.set_ylim(
        0.0,
        upper_limit * 1.18,
    )

    fig.tight_layout()

    output_path = paths.FIGURES_DIR / "ssdi_gas_performance_log_mse.png"

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)
