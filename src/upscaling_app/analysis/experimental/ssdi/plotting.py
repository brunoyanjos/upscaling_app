from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.plotting.colors import (
    GRAY_COLORS,
    get_base_color,
)
from upscaling_app.plotting.style import apply_plot_style

TREATMENT_COLORS = {
    "Untreated": get_base_color("untreated"),
    "SSDI-C9500": get_base_color("corexit"),
    "SSDI-IBC": get_base_color("finasol"),
}


VARIABLE_LABELS = {
    "weber": r"Weber number, $We$",
    "capillary": r"Capillary number, $Ca$",
    "modified_weber": r"Modified Weber number, $We^*$",
}


SPEARMAN_LABELS = {
    "volumetric_velocity": "Volumetric velocity",
    "modified_velocity": "Modified velocity",
    "effective_velocity": "Effective velocity",
    "froude": "Froude number",
    "reynolds": "Reynolds number",
    "weber": "Weber number",
    "capillary": "Capillary number",
}


def _plot_group(
    ax: plt.Axes,
    data: pd.DataFrame,
    *,
    x: str,
) -> None:
    untreated = data.loc[data["dispersion_kind"] == "Untreated"]

    if not untreated.empty:
        ax.scatter(
            untreated[x],
            untreated["d50_D"],
            color=TREATMENT_COLORS["Untreated"],
            label="Untreated",
            alpha=0.75,
        )

    for treatment in (
        "SSDI-C9500",
        "SSDI-IBC",
    ):
        subset = data.loc[data["dispersion_tag"] == treatment]

        if subset.empty:
            continue

        ax.scatter(
            subset[x],
            subset["d50_D"],
            color=TREATMENT_COLORS[treatment],
            label=treatment.removeprefix("SSDI-"),
            alpha=0.75,
        )


def _save_relation_plot(
    data: pd.DataFrame,
    metrics: pd.Series,
    *,
    variable: str,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    valid = (
        data[variable].notna()
        & data["d50_D"].notna()
        & np.isfinite(data[variable])
        & np.isfinite(data["d50_D"])
        & (data[variable] > 0.0)
        & (data["d50_D"] > 0.0)
    )

    plot_data = data.loc[valid].copy()

    if plot_data.empty:
        raise ValueError(f"No valid data available for {variable!r}.")

    fig, ax = plt.subplots(
        figsize=(8, 7),
    )

    _plot_group(
        ax,
        plot_data,
        x=variable,
    )

    x_fit = np.logspace(
        np.log10(plot_data[variable].min()),
        np.log10(plot_data[variable].max()),
        200,
    )

    y_fit = 10.0 ** float(metrics["intercept"]) * x_fit ** float(metrics["slope"])

    ax.plot(
        x_fit,
        y_fit,
        color=GRAY_COLORS["regression"],
        linestyle="--",
        linewidth=2.0,
        label="Log-log fit",
    )

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlabel(VARIABLE_LABELS[variable])
    ax.set_ylabel(r"$d_{50}/D$")

    ax.text(
        0.05,
        0.05,
        (
            f"Slope = {metrics['slope']:.3f}\n"
            f"$R^2_{{\\log}}$ = {metrics['r2_log']:.3f}"
        ),
        transform=ax.transAxes,
        va="bottom",
    )

    ax.grid(
        True,
        which="both",
        alpha=0.3,
    )
    ax.set_axisbelow(True)

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_ssdi_relation_plots(
    data: pd.DataFrame,
    relation_summary: pd.DataFrame,
    output_dir: Path,
) -> None:
    subsets = {
        "pooled": data,
        "ssdi_only": data.loc[data["dispersion_kind"] == "SSDI"].reset_index(drop=True),
    }

    variables = {
        "pooled": (
            "weber",
            "capillary",
            "modified_weber",
        ),
        "ssdi_only": (
            "weber",
            "capillary",
        ),
    }

    for subset_name, subset in subsets.items():
        subset_dir = output_dir / subset_name

        for variable in variables[subset_name]:
            metrics = relation_summary.loc[
                (relation_summary["subset"] == subset_name)
                & (relation_summary["variable"] == variable)
            ]

            if metrics.empty:
                raise ValueError(
                    f"Missing relation metrics for " f"{subset_name!r}, {variable!r}."
                )

            _save_relation_plot(
                subset,
                metrics.iloc[0],
                variable=variable,
                output=subset_dir / f"d50D_vs_{variable}.png",
            )


def save_ssdi_spearman_plot(
    summary: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    pooled = summary.loc[summary["subset"] == "pooled"].set_index("variable")

    ssdi = summary.loc[summary["subset"] == "ssdi_only"].set_index("variable")

    variables = pooled["abs_spearman_rho"].sort_values().index.tolist()

    y = np.arange(len(variables))
    height = 0.34

    fig, ax = plt.subplots(
        figsize=(9, 7),
    )

    ax.barh(
        y - height / 2,
        pooled.loc[variables, "spearman_rho"],
        height=height,
        color=GRAY_COLORS["medium"],
        label="Pooled",
    )

    ax.barh(
        y + height / 2,
        ssdi.loc[variables, "spearman_rho"],
        height=height,
        color=GRAY_COLORS["dark"],
        label="SSDI only",
    )

    ax.set_yticks(y)
    ax.set_yticklabels(
        [
            SPEARMAN_LABELS.get(
                variable,
                variable,
            )
            for variable in variables
        ]
    )

    ax.axvline(
        0.0,
        color=GRAY_COLORS["identity"],
        linestyle="--",
        linewidth=1.5,
    )

    ax.set_xlim(
        -1.0,
        1.0,
    )

    ax.set_xlabel(r"Spearman correlation with $d_{50}/D$, $\rho_s$")

    ax.grid(
        axis="x",
        alpha=0.3,
    )
    ax.set_axisbelow(True)

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_ssdi_dispersant_comparison_plot(
    comparison: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = comparison.sort_values("oil_id").reset_index(drop=True)

    y = np.arange(len(data))

    fig, ax = plt.subplots(
        figsize=(9, 7),
    )

    for index, row in data.iterrows():
        ax.plot(
            [
                row["ibc_reduction_pct"],
                row["c9500_reduction_pct"],
            ],
            [
                index,
                index,
            ],
            color=GRAY_COLORS["medium"],
            linewidth=1.5,
            zorder=1,
        )

    ax.scatter(
        data["c9500_reduction_pct"],
        y,
        color=TREATMENT_COLORS["SSDI-C9500"],
        label="C9500",
        zorder=3,
    )

    ax.scatter(
        data["ibc_reduction_pct"],
        y,
        color=TREATMENT_COLORS["SSDI-IBC"],
        label="IBC",
        zorder=3,
    )

    ax.set_yticks(y)
    ax.set_yticklabels(data["oil_id"].astype(str))

    ax.set_xlabel(r"Median $d_{50}$ reduction [%]")
    ax.set_ylabel("Oil")

    ax.grid(
        axis="x",
        alpha=0.3,
    )
    ax.set_axisbelow(True)

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(fig)
