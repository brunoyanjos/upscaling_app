from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

from upscaling_app import paths
from upscaling_app.plotting.colors import (
    get_base_color,
    get_gray,
    get_regime_color,
    get_ssmd_fraction_color,
)
from upscaling_app.plotting.style import apply_plot_style
from upscaling_app.upscaling.ssmd.versions import (
    REGRESSED_CD_GLOBAL,
    REGRESSED_OIL_WISE,
    SINTEF_BASELINE,
)

MODEL_LABELS = {
    SINTEF_BASELINE: "SINTEF reference",
    REGRESSED_CD_GLOBAL: r"Global regressed $c,d$",
    REGRESSED_OIL_WISE: "Oil-wise calibration",
}

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

REGIME_MARKERS = {
    "3 mm — no gas": "s",
    "2 mm — no gas": "o",
    "2 mm — gas": "^",
}


def _log_mse(
    measured: pd.Series,
    predicted: pd.Series,
) -> float:
    residual = np.log(measured) - np.log(predicted)
    return float(np.mean(residual**2))


def _r2_log(
    measured: pd.Series,
    predicted: pd.Series,
) -> float:
    y = np.log(measured.to_numpy())
    y_pred = np.log(predicted.to_numpy())
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return float(1.0 - ss_res / ss_tot)


def _build_shared_limits(
    data: pd.DataFrame,
) -> tuple[float, float]:
    values = np.concatenate(
        [
            data["dR_exp"].to_numpy(),
            data["dR_pred"].to_numpy(),
        ]
    )
    values = values[np.isfinite(values) & (values > 0.0)]
    return (
        values.min() * 0.90,
        values.max() * 1.10,
    )


def save_ssmd_parity_plot(
    data: pd.DataFrame,
    *,
    model_version: str,
    limits: tuple[float, float],
    output: Path,
) -> None:
    apply_plot_style()
    output.parent.mkdir(parents=True, exist_ok=True)

    model_data = data.loc[
        data["model_version"] == model_version
    ].copy()

    valid = (
        model_data["dR_exp"].notna()
        & model_data["dR_pred"].notna()
        & np.isfinite(model_data["dR_exp"])
        & np.isfinite(model_data["dR_pred"])
        & (model_data["dR_exp"] > 0.0)
        & (model_data["dR_pred"] > 0.0)
    )
    model_data = model_data.loc[valid].copy()

    if model_data.empty:
        raise ValueError(
            f"No valid SSMD predictions found for {model_version!r}."
        )

    log_mse = _log_mse(
        model_data["dR_exp"],
        model_data["dR_pred"],
    )
    r2_log = _r2_log(
        model_data["dR_exp"],
        model_data["dR_pred"],
    )

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.scatter(
        model_data["dR_exp"],
        model_data["dR_pred"],
        color=get_base_color("ssmd"),
        alpha=0.75,
        zorder=3,
    )

    ax.plot(
        limits,
        limits,
        color=get_gray("identity"),
        linestyle="--",
        linewidth=2.0,
        label=r"$y=x$",
        zorder=2,
    )

    ax.text(
        0.05,
        0.95,
        f"Log-MSE = {log_mse:.3f}\n$R^2_{{\\log}}$ = {r2_log:.3f}",
        transform=ax.transAxes,
        va="top",
    )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(limits)
    ax.set_ylim(limits)
    ax.set_xlabel(r"Experimental $d_R$")
    ax.set_ylabel(r"Predicted $d_R$")
    ax.grid(True, which="both", linestyle="--", color=get_gray("grid"), alpha=0.6)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_ssmd_reference_vs_global_parity(
    predictions: pd.DataFrame,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    model_versions = [SINTEF_BASELINE, REGRESSED_CD_GLOBAL]
    comparison = predictions.loc[
        predictions["model_version"].isin(model_versions)
    ].copy()
    limits = _build_shared_limits(comparison)

    save_ssmd_parity_plot(
        comparison,
        model_version=SINTEF_BASELINE,
        limits=limits,
        output=(output_dir / "ssmd_parity_sintef.png"),
    )
    save_ssmd_parity_plot(
        comparison,
        model_version=REGRESSED_CD_GLOBAL,
        limits=limits,
        output=(output_dir / "ssmd_parity_regressed_cd_global.png"),
    )


def save_ssmd_model_parity_comparison(
    predictions: pd.DataFrame,
    overall: pd.DataFrame,
) -> None:
    apply_plot_style()
    paths.SSMD_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    limits = _build_shared_limits(predictions)
    metrics = overall.set_index("model")

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(16, 5.8),
        sharex=True,
        sharey=True,
    )

    for ax, model in zip(axes, MODEL_ORDER):
        model_data = predictions.loc[
            predictions["model"] == model
        ].copy()

        for (regime, fraction), group in model_data.groupby(
            ["regime", "water_jet_fraction"],
            sort=False,
        ):
            ax.scatter(
                group["dR_exp"],
                group["dR_pred"],
                color=get_ssmd_fraction_color(float(fraction)),
                marker=REGIME_MARKERS[str(regime)],
                s=52,
                alpha=0.88,
                edgecolors=get_gray("dark"),
                linewidths=0.35,
                zorder=3,
            )

        ax.plot(
            limits,
            limits,
            color=get_gray("identity"),
            linestyle="--",
            linewidth=1.6,
            zorder=1,
        )

        row = metrics.loc[model]
        metric_text = (
            f"Log-MSE = {row['log_mse']:.3f}\n"
            f"$R^2$ = {row['r2']:.3f}\n"
            f"RMSE = {row['rmse']:.3f}\n"
            f"MAPE = {row['mape']:.1f}%"
        )

        ax.text(
            0.05,
            0.95,
            metric_text,
            transform=ax.transAxes,
            va="top",
        )

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(limits)
        ax.set_ylim(limits)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(MODEL_TITLES[model])
        ax.set_xlabel(r"Measured $d_R$")
        ax.grid(
            True,
            which="both",
            linestyle="--",
            color=get_gray("grid"),
            alpha=0.6,
        )
        ax.set_axisbelow(True)

    axes[0].set_ylabel(r"Predicted $d_R$")
    axes[2].text(
        0.95,
        0.05,
        "In-sample calibration",
        transform=axes[2].transAxes,
        ha="right",
        va="bottom",
        fontsize=10,
        color=get_gray("regression"),
    )

    fractions = sorted(
        predictions["water_jet_fraction"].dropna().unique()
    )
    fraction_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markerfacecolor=get_ssmd_fraction_color(float(fraction)),
            markeredgecolor="none",
            markersize=8,
            label=f"{fraction:.0%} water jet",
        )
        for fraction in fractions
    ]

    regime_handles = [
        Line2D(
            [0],
            [0],
            marker=marker,
            linestyle="none",
            color=get_gray("dark"),
            markerfacecolor="white",
            markersize=8,
            label=regime,
        )
        for regime, marker in REGIME_MARKERS.items()
    ]

    fig.legend(
        handles=fraction_handles + regime_handles,
        loc="lower center",
        ncol=4,
        frameon=False,
    )

    fig.tight_layout(rect=[0.0, 0.15, 1.0, 1.0])
    fig.savefig(
        paths.SSMD_FIGURES_DIR / "ssmd_model_parity_comparison.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def save_ssmd_regime_performance_plot(
    by_regime: pd.DataFrame,
) -> None:
    apply_plot_style()
    paths.SSMD_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    model_order = MODEL_ORDER
    regime_order = list(REGIME_MARKERS)

    pivot = by_regime.pivot(
        index="model",
        columns="regime",
        values="log_mse",
    ).reindex(model_order)

    x = np.arange(len(model_order))
    width = 0.24

    fig, ax = plt.subplots(figsize=(9, 6))

    regime_colors = {
        "3 mm — no gas": get_regime_color("ssmd", tone=700),
        "2 mm — no gas": get_regime_color("ssmd", tone=500),
        "2 mm — gas": get_regime_color("ssmd", tone=300),
    }

    for offset, regime in zip([-1, 0, 1], regime_order):
        bars = ax.bar(
            x + offset * width,
            pivot[regime],
            width,
            label=regime,
            color=regime_colors[regime],
        )
        ax.bar_label(
            bars,
            fmt="%.3f",
            padding=3,
            fontsize=9,
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
    ax.set_title("SSMD prediction performance by experimental regime")
    ax.legend(frameon=False)
    ax.grid(
        axis="y",
        linestyle="--",
        color=get_gray("grid"),
        alpha=0.7,
    )
    ax.set_axisbelow(True)
    ax.set_ylim(0.0, float(np.nanmax(pivot.to_numpy())) * 1.20)
    fig.tight_layout()
    fig.savefig(
        paths.SSMD_FIGURES_DIR / "ssmd_regime_performance_log_mse.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)
