from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from upscaling_app.plotting.colors import (
    get_base_color,
    get_gray,
)
from upscaling_app.plotting.style import (
    apply_plot_style,
)

CONDITION_MARKERS = {
    (0.002, False): "o",
    (0.003, False): "s",
    (0.002, True): "^",
}


CONDITION_LABELS = {
    (0.002, False): "2 mm — no gas",
    (0.003, False): "3 mm — no gas",
    (0.002, True): "2 mm — gas",
}


FEATURE_LABELS = {
    "froude": "Froude number",
    "reynolds": "Reynolds number",
    "weber": "Weber number",
    "untreated_froude": "Untreated Froude number",
    "momentum_amplification": "Momentum amplification",
    "kinetic_power_ratio": "Kinetic power ratio",
}


SSDI_COLORS = {
    "SSDI-C9500": get_base_color("ssdi_corexit"),
    "SSDI-IBC": get_base_color("ssdi_finasol"),
}


def _save_log_shape_relation(
    data: pd.DataFrame,
    *,
    feature: str,
    output: Path,
    color_column: str | None = None,
    color_map: dict[str, str] | None = None,
    default_color: str,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    for condition, marker in CONDITION_MARKERS.items():
        nozzle_diameter, has_gas = condition

        condition_data = data.loc[
            data["nozzle_diameter"].eq(nozzle_diameter) & data["has_gas"].eq(has_gas)
        ]

        if condition_data.empty:
            continue

        if color_column is None or color_map is None:
            ax.scatter(
                condition_data[feature],
                condition_data["shape"],
                marker=marker,
                s=55,
                alpha=0.8,
                color=default_color,
                label=CONDITION_LABELS[condition],
            )

            continue

        for color_value, subset in condition_data.groupby(
            color_column,
            sort=False,
        ):
            color = color_map.get(
                str(color_value),
                default_color,
            )

            ax.scatter(
                subset[feature],
                subset["shape"],
                marker=marker,
                s=55,
                alpha=0.8,
                color=color,
                label=(f"{color_value} — " f"{CONDITION_LABELS[condition]}"),
            )

    ax.set_xscale("log")

    ax.set_yscale("log")

    ax.set_xlabel(FEATURE_LABELS[feature])

    ax.set_ylabel(r"Rosin–Rammler shape parameter, $k$")

    ax.grid(
        color=get_gray("grid"),
        alpha=0.7,
    )

    ax.legend(
        fontsize=9,
    )

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_untreated_shape_relations(
    data: pd.DataFrame,
    output_dir: Path,
) -> None:
    untreated = data.loc[data["dispersion_kind"].eq("Untreated")]

    for feature in [
        "froude",
        "reynolds",
        "weber",
    ]:
        _save_log_shape_relation(
            untreated,
            feature=feature,
            output=(output_dir / "untreated" / f"k_vs_{feature}.png"),
            default_color=get_base_color("untreated"),
        )


def save_ssdi_shape_relations(
    data: pd.DataFrame,
    output_dir: Path,
) -> None:
    ssdi = data.loc[data["dispersion_kind"].eq("SSDI")]

    for feature in [
        "reynolds",
        "weber",
    ]:
        _save_log_shape_relation(
            ssdi,
            feature=feature,
            output=(output_dir / "ssdi" / f"k_vs_{feature}.png"),
            color_column="dispersion_tag",
            color_map=SSDI_COLORS,
            default_color=get_gray("dark"),
        )


def save_ssmd_shape_relations(
    data: pd.DataFrame,
    output_dir: Path,
) -> None:
    ssmd = data.loc[data["dispersion_kind"].eq("SSMD")]

    for feature in [
        "untreated_froude",
        "momentum_amplification",
        "kinetic_power_ratio",
    ]:
        _save_log_shape_relation(
            ssmd,
            feature=feature,
            output=(output_dir / "ssmd" / f"k_vs_{feature}.png"),
            default_color=get_base_color("ssmd"),
        )
