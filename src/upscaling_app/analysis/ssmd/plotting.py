from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.plotting.style import (
    APPLE_COLORS,
    APPLE_GRAYS,
    PRESENTATION_COLORS,
    apply_plot_style,
)
from upscaling_app.upscaling.ssmd.versions import (
    REGRESSED_CD_GLOBAL,
    SINTEF_BASELINE,
)

MODEL_LABELS = {
    SINTEF_BASELINE: "SINTEF reference",
    REGRESSED_CD_GLOBAL: r"Global regressed $c,d$",
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

    minimum = values.min()
    maximum = values.max()

    return (
        minimum * 0.90,
        maximum * 1.10,
    )


def save_ssmd_parity_plot(
    data: pd.DataFrame,
    *,
    model_version: str,
    limits: tuple[float, float],
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_data = data.loc[data["model_version"] == model_version].copy()

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
        raise ValueError("No valid SSMD predictions found for " f"{model_version!r}.")

    log_mse = _log_mse(
        model_data["dR_exp"],
        model_data["dR_pred"],
    )

    r2_log = _r2_log(
        model_data["dR_exp"],
        model_data["dR_pred"],
    )

    fig, ax = plt.subplots(
        figsize=(8, 8),
    )

    ax.scatter(
        model_data["dR_exp"],
        model_data["dR_pred"],
        color=PRESENTATION_COLORS["Azul"],
        alpha=0.70,
        zorder=3,
    )

    ax.plot(
        limits,
        limits,
        color=PRESENTATION_COLORS["Cinza"],
        linestyle="--",
        linewidth=2.0,
        label=r"$y=x$",
        zorder=2,
    )

    metric_text = f"Log-MSE = {log_mse:.3f}\n" f"$R^2_{{\\log}}$ = {r2_log:.3f}"

    ax.text(
        0.05,
        0.95,
        metric_text,
        transform=ax.transAxes,
        verticalalignment="top",
    )

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlim(limits)
    ax.set_ylim(limits)

    ax.set_xlabel(r"Experimental $d_R$")

    ax.set_ylabel(r"Predicted $d_R$")

    ax.grid(
        True,
        which="both",
        linestyle="--",
        alpha=0.3,
    )

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_ssmd_reference_vs_global_parity(
    predictions: pd.DataFrame,
    output_dir: Path,
) -> None:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_versions = [
        SINTEF_BASELINE,
        REGRESSED_CD_GLOBAL,
    ]

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
