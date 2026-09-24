from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.plotting.style import (
    APPLE_COLORS,
    PRESENTATION_COLORS,
    APPLE_GRAYS,
    apply_plot_style,
)

REGIME_COLORS = {
    "Untreated": APPLE_COLORS["blue"],
    "SSDI": APPLE_COLORS["red"],
}


# ============================================================
# SSDI experimental relations
# ============================================================


def save_experimental_relation_plot(
    data: pd.DataFrame,
    metrics: dict[str, float],
    *,
    x: str,
    xlabel: str,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    valid = (
        data[x].notna()
        & data["d50_D"].notna()
        & np.isfinite(data[x])
        & np.isfinite(data["d50_D"])
        & (data[x] > 0.0)
        & (data["d50_D"] > 0.0)
    )

    plot_data = data.loc[valid].copy()

    fig, ax = plt.subplots(
        figsize=(8, 8),
    )

    for kind, group in plot_data.groupby(
        "dispersion_kind",
        sort=False,
    ):
        ax.scatter(
            group[x],
            group["d50_D"],
            color=REGIME_COLORS.get(
                kind,
                APPLE_GRAYS["gray"],
            ),
            label=kind,
            alpha=0.75,
        )

    x_fit = np.logspace(
        np.log10(plot_data[x].min()),
        np.log10(plot_data[x].max()),
        200,
    )

    y_fit = 10.0 ** metrics["intercept"] * x_fit ** metrics["slope"]

    ax.plot(
        x_fit,
        y_fit,
        color=APPLE_GRAYS["gray"],
        linestyle="--",
        label="Log-log fit",
    )

    ax.set_xscale("log")
    ax.set_yscale("log")

    metric_text = (
        f"Slope = {metrics['slope']:.3f}\n"
        f"$R^2_{{\\log}}$ = "
        f"{metrics['r2_log']:.3f}"
    )

    ax.text(
        0.05,
        0.05,
        metric_text,
        transform=ax.transAxes,
        verticalalignment="bottom",
    )

    ax.set_xlabel(xlabel)

    ax.set_ylabel(r"$d_{50}/D$")

    ax.legend()

    ax.grid(
        True,
        which="both",
        linestyle="--",
        alpha=0.3,
    )

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_ssdi_experimental_plots(
    data: pd.DataFrame,
    relation_summary: pd.DataFrame,
    output_dir: Path,
) -> None:
    relations = {
        "weber": (
            "Weber number, $We$",
            "d50D_vs_weber.png",
        ),
        "capillary": (
            "Capillary number, $Ca$",
            "d50D_vs_capillary.png",
        ),
        "modified_weber": (
            r"Modified Weber number, $We^*$ ($B=0.08$)",
            "d50D_vs_modified_weber.png",
        ),
    }

    subsets = {
        "pooled": data,
        "ssdi_only": (
            data.loc[data["dispersion_kind"] == "SSDI"].reset_index(drop=True)
        ),
    }

    for subset_name, subset in subsets.items():
        subset_dir = output_dir / subset_name

        subset_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        for variable, (
            xlabel,
            filename,
        ) in relations.items():
            row = relation_summary.loc[
                (relation_summary["subset"] == subset_name)
                & (relation_summary["variable"] == variable)
            ]

            if row.empty:
                raise ValueError(
                    "Missing relation metrics for " f"{subset_name=} and {variable=}."
                )

            row = row.iloc[0]

            metrics = {
                "slope": float(row["slope"]),
                "intercept": float(row["intercept"]),
                "r2_log": float(row["r2_log"]),
            }

            save_experimental_relation_plot(
                subset,
                metrics,
                x=variable,
                xlabel=xlabel,
                output=(subset_dir / filename),
            )


# ============================================================
# Treatment-effect analysis
# ============================================================


def save_treatment_reduction_summary_plot(
    summary: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = summary.sort_values(
        "median_reduction_pct",
        ascending=False,
    )

    fig, ax = plt.subplots(
        figsize=(8, 8),
    )

    ax.bar(
        data["dispersion_tag"],
        data["median_reduction_pct"],
        color=PRESENTATION_COLORS["Azul"],
    )

    ax.set_ylabel(r"Median $d_{50}$ reduction [%]")

    ax.tick_params(
        axis="x",
        rotation=45,
    )

    ax.axhline(
        0.0,
        color=PRESENTATION_COLORS["Cinza"],
        linestyle="--",
    )

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.3,
    )

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_treatment_variability_plot(
    summary: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    treatment_order = (
        summary.groupby("dispersion_tag")["median_reduction_pct"]
        .median()
        .sort_values(ascending=False)
        .index.tolist()
    )

    values = [
        summary.loc[
            summary["dispersion_tag"] == treatment,
            "median_reduction_pct",
        ].to_numpy()
        for treatment in treatment_order
    ]

    fig, ax = plt.subplots(
        figsize=(10, 7),
    )

    ax.boxplot(
        values,
        tick_labels=treatment_order,
        showfliers=False,
    )

    for index, treatment in enumerate(
        treatment_order,
        start=1,
    ):
        group = summary.loc[summary["dispersion_tag"] == treatment]

        regular = group.loc[~group["is_outlier"]]

        outliers = group.loc[group["is_outlier"]]

        ax.scatter(
            [index] * len(regular),
            regular["median_reduction_pct"],
            color=PRESENTATION_COLORS["Azul"],
            alpha=0.75,
        )

        ax.scatter(
            [index] * len(outliers),
            outliers["median_reduction_pct"],
            color=PRESENTATION_COLORS["Laranja"],
            alpha=0.9,
            zorder=3,
        )

        for _, row in outliers.iterrows():
            ax.annotate(
                str(row["oil_id"]),
                (
                    index,
                    row["median_reduction_pct"],
                ),
                xytext=(6, 0),
                textcoords="offset points",
                va="center",
            )

    ax.set_ylabel(r"$d_{50}$ reduction [%]")

    ax.tick_params(
        axis="x",
        rotation=45,
    )

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.3,
    )

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_treatment_extremes_plot(
    best: pd.DataFrame,
    worst: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    worst = worst.sort_values(
        "median_reduction_pct",
        ascending=True,
    )

    best = best.sort_values(
        "median_reduction_pct",
        ascending=True,
    )

    extremes = pd.concat(
        [
            worst,
            best,
        ],
        ignore_index=True,
    )

    labels = extremes["oil_id"].astype(str) + " — " + extremes["dispersion_tag"]

    colors = [PRESENTATION_COLORS["Laranja"]] * len(worst) + [
        PRESENTATION_COLORS["Azul"]
    ] * len(best)

    fig, ax = plt.subplots(
        figsize=(9, 7),
    )

    ax.barh(
        labels,
        extremes["median_reduction_pct"],
        color=colors,
    )

    ax.set_xlabel(r"$d_{50}$ reduction [%]")

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.3,
    )

    for index, value in enumerate(extremes["median_reduction_pct"]):
        ax.text(
            value + 0.5,
            index,
            f"{value:.1f}%",
            va="center",
        )

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_water_jet_intensity_plot(
    by_oil: pd.DataFrame,
    by_fraction: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(9, 7),
    )

    first_oil = True

    for _, group in by_oil.groupby("oil_id"):
        group = group.sort_values("water_jet_pct")

        ax.plot(
            group["water_jet_pct"],
            group["median_reduction_pct"],
            marker="o",
            color=PRESENTATION_COLORS["Cinza"],
            alpha=0.35,
            linewidth=1.0,
            label=("Individual oils" if first_oil else None),
        )

        first_oil = False

    ax.plot(
        by_fraction["water_jet_pct"],
        by_fraction["median_reduction_pct"],
        marker="o",
        color=PRESENTATION_COLORS["Azul"],
        linewidth=2.5,
        label="Median across oils",
        zorder=3,
    )

    ax.set_xlabel("Water-jet fraction [%]")

    ax.set_ylabel(r"$d_{50}$ reduction [%]")

    ax.set_xticks(by_fraction["water_jet_pct"])

    ax.grid(
        True,
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


def save_ssdi_dispersant_comparison_plot(
    comparison: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = comparison.sort_values("delta_pct_points").reset_index(drop=True)

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
            color=PRESENTATION_COLORS["Cinza"],
            linewidth=1.5,
            alpha=0.7,
            zorder=1,
        )

    ax.scatter(
        data["c9500_reduction_pct"],
        y,
        color=PRESENTATION_COLORS["Azul"],
        label="C9500",
        zorder=3,
    )

    ax.scatter(
        data["ibc_reduction_pct"],
        y,
        color=PRESENTATION_COLORS["Laranja"],
        label="IBC",
        zorder=3,
    )

    ax.set_yticks(y)

    ax.set_yticklabels(data["oil_id"].astype(str))

    ax.set_xlabel(r"$d_{50}$ reduction [%]")

    ax.set_ylabel("Oil")

    ax.grid(
        axis="x",
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


def save_ssdi_spearman_plot(
    summary: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    labels = {
        "volumetric_velocity": "Volumetric velocity",
        "modified_velocity": "Modified velocity",
        "effective_velocity": "Effective velocity",
        "froude": "Froude number",
        "reynolds": "Reynolds number",
        "weber": "Weber number",
        "capillary": "Capillary number",
    }

    data = summary.copy().sort_values(
        "spearman_rho",
        ascending=True,
    )

    y_labels = [
        labels.get(
            variable,
            variable,
        )
        for variable in data["variable"]
    ]

    fig, ax = plt.subplots(
        figsize=(9, 7),
    )

    ax.barh(
        y_labels,
        data["spearman_rho"],
        color=APPLE_COLORS["blue"],
    )

    ax.axvline(
        0.0,
        color=APPLE_GRAYS["gray"],
        linestyle="--",
    )

    for index, value in enumerate(data["spearman_rho"]):
        offset = 0.02 if value >= 0.0 else -0.02

        alignment = "left" if value >= 0.0 else "right"

        ax.text(
            value + offset,
            index,
            f"{value:.2f}",
            va="center",
            ha=alignment,
        )

    ax.set_xlabel(r"Spearman correlation with $d_{50}/D$, $\rho_s$")

    ax.set_xlim(
        -1.0,
        1.0,
    )

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.3,
    )

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


SSMD_REGIME_COLORS = {
    "2 mm — no gas": APPLE_COLORS["blue"],
    "3 mm — no gas": APPLE_GRAYS["gray"],
    "2 mm — gas": APPLE_COLORS["red"],
}


def save_ssmd_regime_response_plot(
    summary: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(9, 7),
    )

    regime_order = [
        "2 mm — no gas",
        "3 mm — no gas",
        "2 mm — gas",
    ]

    for regime in regime_order:
        group = summary.loc[summary["regime"] == regime].sort_values("water_jet_pct")

        if group.empty:
            continue

        color = SSMD_REGIME_COLORS[regime]

        ax.plot(
            group["water_jet_pct"],
            group["median_reduction_pct"],
            marker="o",
            color=color,
            linewidth=2.5,
            label=regime,
            zorder=3,
        )

        ax.fill_between(
            group["water_jet_pct"],
            group["q1_reduction_pct"],
            group["q3_reduction_pct"],
            color=color,
            alpha=0.12,
            linewidth=0.0,
            zorder=1,
        )

    ax.set_xlabel("Water-jet fraction [%]")

    ax.set_ylabel(r"Median $d_{50}$ reduction [%]")

    ax.set_xticks([40, 45, 50, 55])

    ax.grid(
        True,
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


def save_ssmd_gas_effect_plot(
    summary: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    regimes = {
        "2 mm — no gas": APPLE_COLORS["blue"],
        "2 mm — gas": APPLE_COLORS["red"],
    }

    data = summary.loc[summary["regime"].isin(regimes)].copy()

    fig, ax = plt.subplots(
        figsize=(9, 7),
    )

    for regime, color in regimes.items():
        group = data.loc[data["regime"] == regime].sort_values("water_jet_pct")

        ax.plot(
            group["water_jet_pct"],
            group["median_reduction_pct"],
            marker="o",
            color=color,
            linewidth=2.5,
            label=regime,
            zorder=3,
        )

        ax.fill_between(
            group["water_jet_pct"],
            group["q1_reduction_pct"],
            group["q3_reduction_pct"],
            color=color,
            alpha=0.12,
            linewidth=0.0,
            zorder=1,
        )

    no_gas = data.loc[
        data["regime"] == "2 mm — no gas",
        [
            "water_jet_pct",
            "median_reduction_pct",
        ],
    ].rename(
        columns={
            "median_reduction_pct": ("no_gas_reduction"),
        }
    )

    gas = data.loc[
        data["regime"] == "2 mm — gas",
        [
            "water_jet_pct",
            "median_reduction_pct",
        ],
    ].rename(
        columns={
            "median_reduction_pct": ("gas_reduction"),
        }
    )

    comparison = no_gas.merge(
        gas,
        on="water_jet_pct",
        validate="one_to_one",
    )

    comparison["delta"] = comparison["gas_reduction"] - comparison["no_gas_reduction"]

    for _, row in comparison.iterrows():
        midpoint = (row["gas_reduction"] + row["no_gas_reduction"]) / 2.0

        ax.text(
            row["water_jet_pct"] + 0.4,
            midpoint,
            f"{row['delta']:.1f} p.p.",
            color=APPLE_GRAYS["gray"],
            va="center",
        )

    ax.set_xlabel("Water-jet fraction [%]")

    ax.set_ylabel(r"Median $d_{50}$ reduction [%]")

    ax.set_xticks([40, 45, 50])

    ax.grid(
        True,
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


def save_ssmd_momentum_spearman_plot(
    summary: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    regime_order = [
        "3 mm — no gas",
        "2 mm — gas",
        "2 mm — no gas",
    ]

    colors = {
        "2 mm — no gas": APPLE_COLORS["blue"],
        "3 mm — no gas": APPLE_GRAYS["gray"],
        "2 mm — gas": APPLE_COLORS["red"],
    }

    data = summary.set_index("regime").loc[regime_order].reset_index()

    y = np.arange(len(data))

    ax_colors = [colors[regime] for regime in data["regime"]]

    fig, ax = plt.subplots(
        figsize=(9, 7),
    )

    ax.barh(
        y,
        data["spearman_rho"],
        color=ax_colors,
    )

    ax.axvline(
        0.0,
        color=APPLE_GRAYS["gray"],
        linestyle="--",
    )

    for index, value in enumerate(data["spearman_rho"]):
        ax.text(
            value - 0.03,
            index,
            f"{value:.2f}",
            va="center",
            ha="right",
        )

    ax.set_yticks(y)

    ax.set_yticklabels(data["regime"])

    ax.set_xlabel(r"Spearman correlation with $d_R$, $\rho_s$")

    ax.set_xlim(
        -1.0,
        0.2,
    )

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.3,
    )

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_ssmd_momentum_response_plot(
    data: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    regime_order = [
        "2 mm — no gas",
        "3 mm — no gas",
        "2 mm — gas",
    ]

    colors = {
        "2 mm — no gas": APPLE_COLORS["blue"],
        "3 mm — no gas": APPLE_GRAYS["gray"],
        "2 mm — gas": APPLE_COLORS["red"],
    }

    fig, ax = plt.subplots(
        figsize=(9, 7),
    )

    for regime in regime_order:
        group = data.loc[data["regime"] == regime].copy()

        valid = (
            (group["momentum_amplification"] > 0.0)
            & (group["dR_measured"] > 0.0)
            & np.isfinite(group["momentum_amplification"])
            & np.isfinite(group["dR_measured"])
        )

        group = group.loc[valid]

        if group.empty:
            continue

        x = np.log10(group["momentum_amplification"].to_numpy())

        y = np.log10(group["dR_measured"].to_numpy())

        slope, intercept = np.polyfit(
            x,
            y,
            1,
        )

        y_pred = intercept + slope * x

        ss_res = np.sum((y - y_pred) ** 2)

        ss_tot = np.sum((y - y.mean()) ** 2)

        r2_log = 1.0 - ss_res / ss_tot

        color = colors[regime]

        ax.scatter(
            group["momentum_amplification"],
            group["dR_measured"],
            color=color,
            alpha=0.65,
            zorder=3,
        )

        x_fit = np.logspace(
            np.log10(group["momentum_amplification"].min()),
            np.log10(group["momentum_amplification"].max()),
            200,
        )

        y_fit = 10.0**intercept * x_fit**slope

        ax.plot(
            x_fit,
            y_fit,
            color=color,
            linewidth=2.5,
            label=(
                f"{regime}: " f"slope={slope:.2f}, " rf"$R^2_{{\log}}$={r2_log:.2f}"
            ),
        )

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlabel(r"Momentum amplification, $A_M$")

    ax.set_ylabel(r"Relative droplet size, $d_R$")

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


def save_ssmd_global_momentum_response_plot(
    data: pd.DataFrame,
    output: Path,
) -> None:
    apply_plot_style()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    colors = {
        "2 mm — no gas": APPLE_COLORS["blue"],
        "3 mm — no gas": APPLE_GRAYS["gray"],
        "2 mm — gas": APPLE_COLORS["red"],
    }

    valid = (
        data["momentum_amplification"].notna()
        & data["dR_measured"].notna()
        & np.isfinite(data["momentum_amplification"])
        & np.isfinite(data["dR_measured"])
        & (data["momentum_amplification"] > 0.0)
        & (data["dR_measured"] > 0.0)
    )

    plot_data = data.loc[valid].copy()

    # ========================================================
    # Global log-log regression
    # ========================================================

    x_log = np.log10(plot_data["momentum_amplification"].to_numpy())

    y_log = np.log10(plot_data["dR_measured"].to_numpy())

    slope, intercept = np.polyfit(
        x_log,
        y_log,
        1,
    )

    y_pred_log = intercept + slope * x_log

    ss_res = np.sum((y_log - y_pred_log) ** 2)

    ss_tot = np.sum((y_log - y_log.mean()) ** 2)

    r2_log = 1.0 - ss_res / ss_tot

    # ========================================================
    # Plot
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(9, 7),
    )

    for regime, group in plot_data.groupby(
        "regime",
        sort=False,
    ):
        ax.scatter(
            group["momentum_amplification"],
            group["dR_measured"],
            color=colors.get(
                regime,
                APPLE_GRAYS["gray"],
            ),
            alpha=0.70,
            label=regime,
            zorder=3,
        )

    x_fit = np.logspace(
        np.log10(plot_data["momentum_amplification"].min()),
        np.log10(plot_data["momentum_amplification"].max()),
        200,
    )

    y_fit = 10.0**intercept * x_fit**slope

    ax.plot(
        x_fit,
        y_fit,
        color=APPLE_GRAYS["gray"],
        linestyle="--",
        linewidth=2.5,
        label="Global log-log fit",
        zorder=2,
    )

    # ========================================================
    # Metrics
    # ========================================================

    metric_text = f"Slope = {slope:.3f}\n" f"$R^2_{{\\log}}$ = {r2_log:.3f}"

    ax.text(
        0.05,
        0.05,
        metric_text,
        transform=ax.transAxes,
        verticalalignment="bottom",
    )

    # ========================================================
    # Style
    # ========================================================

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlabel(r"Momentum amplification, $A_M$")

    ax.set_ylabel(r"Relative droplet size, $d_R$")

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
