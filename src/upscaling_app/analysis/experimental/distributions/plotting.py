from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from upscaling_app.plotting.colors import (
    get_base_color,
    get_gray,
)


def _get_distribution_group(
    dispersion_kind: str,
    dispersion_tag: str,
) -> tuple[str, str]:
    kind = str(dispersion_kind).strip().lower()

    tag = str(dispersion_tag).strip().lower()

    if kind == "untreated":
        return (
            "Untreated",
            get_base_color("untreated"),
        )

    if kind == "ssmd":
        return (
            "SSMD",
            get_base_color("ssmd"),
        )

    if kind == "ssdi":
        if "c9500" in tag:
            return (
                "SSDI — Corexit",
                get_base_color("ssdi_corexit"),
            )

        if "ibc" in tag:
            return (
                "SSDI — Finasol",
                get_base_color("ssdi_finasol"),
            )

    raise ValueError(
        "Unsupported dispersion condition: "
        f"kind={dispersion_kind!r}, "
        f"tag={dispersion_tag!r}."
    )


def _add_plot_groups(
    data: pd.DataFrame,
) -> pd.DataFrame:
    data = data.copy()

    groups = data.apply(
        lambda row: _get_distribution_group(
            dispersion_kind=row["dispersion_kind"],
            dispersion_tag=row["dispersion_tag"],
        ),
        axis=1,
    )

    data["plot_group"] = [group[0] for group in groups]

    data["plot_color"] = [group[1] for group in groups]

    return data


def save_d50_consistency_plot(
    comparison: pd.DataFrame,
    output: Path,
) -> None:
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = comparison[
        [
            "dispersion_kind",
            "dispersion_tag",
            "measured_d50",
            "d50",
        ]
    ].copy()

    data = data.loc[np.isfinite(data["measured_d50"]) & np.isfinite(data["d50"])]

    data["measured_d50_mm"] = data["measured_d50"] * 1e3

    data["reconstructed_d50_mm"] = data["d50"] * 1e3

    data = _add_plot_groups(data)

    minimum = min(
        data["measured_d50_mm"].min(),
        data["reconstructed_d50_mm"].min(),
    )

    maximum = max(
        data["measured_d50_mm"].max(),
        data["reconstructed_d50_mm"].max(),
    )

    margin = 0.05 * (maximum - minimum)

    lower = max(
        0.0,
        minimum - margin,
    )

    upper = maximum + margin

    fig, ax = plt.subplots(
        figsize=(7, 7),
    )

    for (
        plot_group,
        group,
    ) in data.groupby(
        "plot_group",
        sort=False,
    ):
        ax.scatter(
            group["measured_d50_mm"],
            group["reconstructed_d50_mm"],
            color=group["plot_color"].iloc[0],
            alpha=0.8,
            label=plot_group,
        )

    ax.plot(
        [lower, upper],
        [lower, upper],
        color=get_gray("identity"),
        linestyle="--",
        linewidth=1.5,
        label="Identity",
    )

    ax.set_xlim(
        lower,
        upper,
    )

    ax.set_ylim(
        lower,
        upper,
    )

    ax.set_xlabel("Reported D50 [mm]")

    ax.set_ylabel("Reconstructed D50 [mm]")

    ax.grid(
        color=get_gray("grid"),
        alpha=0.8,
    )

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def save_reported_percentile_plot(
    comparison: pd.DataFrame,
    output: Path,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)

    data = comparison[
        [
            "dispersion_kind",
            "dispersion_tag",
            "reported_percentile",
        ]
    ].copy()

    data = data.loc[np.isfinite(data["reported_percentile"])]
    data["deviation"] = (data["reported_percentile"] - 50.0).abs()

    data = data.sort_values("deviation").reset_index(drop=True)
    data["rank"] = np.arange(1, len(data) + 1)

    data = _add_plot_groups(data)

    fig, ax = plt.subplots(figsize=(9, 6))

    for plot_group, group in data.groupby("plot_group", sort=False):
        ax.scatter(
            group["rank"],
            group["reported_percentile"],
            color=group["plot_color"].iloc[0],
            alpha=0.8,
            label=plot_group,
        )

    ax.axhline(
        50.0,
        color=get_gray("identity"),
        linestyle="--",
        linewidth=1.5,
        label="Expected D50 percentile",
    )

    ax.set_xlabel("Experiment rank")
    ax.set_ylabel("CDF at reported D50 [%]")

    ax.set_ylim(0.0, 100.0)

    ax.grid(color=get_gray("grid"), alpha=0.8)

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)
