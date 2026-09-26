from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from upscaling_app.analysis.experimental.treatment_effect.analysis import (
    build_treatment_effects,
    summarize_treatment_by_oil,
)
from upscaling_app.upscaling.ssdi.physics.derived_properties import (
    add_ssdi_physics,
)

REFERENCE_B: Final[float] = 0.08

RELATION_VARIABLES: Final[tuple[str, ...]] = (
    "weber",
    "capillary",
)

SPEARMAN_VARIABLES: Final[tuple[str, ...]] = (
    "volumetric_velocity",
    "modified_velocity",
    "effective_velocity",
    "froude",
    "reynolds",
    "weber",
    "capillary",
)

SSDI_TREATMENTS: Final[tuple[str, ...]] = (
    "SSDI-C9500",
    "SSDI-IBC",
)


def prepare_ssdi_experimental_data(
    data: pd.DataFrame,
) -> pd.DataFrame:
    selected = data.loc[
        data["dispersion_kind"].isin(
            [
                "Untreated",
                "SSDI",
            ]
        )
    ].copy()

    selected = add_ssdi_physics(selected)

    selected["d50_D"] = selected["measured_d50"] / selected["nozzle_diameter"]

    selected["modified_weber"] = selected["weber"] / (
        1.0 + REFERENCE_B * selected["capillary"] * selected["d50_D"] ** (1.0 / 3.0)
    )

    return selected.reset_index(drop=True)


def build_ssdi_dispersant_comparison(
    data: pd.DataFrame,
) -> pd.DataFrame:
    effects = build_treatment_effects(data)

    ssdi_effects = effects.loc[effects["dispersion_kind"] == "SSDI"].copy()

    by_oil = summarize_treatment_by_oil(ssdi_effects)

    comparison = by_oil.loc[
        by_oil["dispersion_tag"].isin(SSDI_TREATMENTS),
        [
            "oil_id",
            "dispersion_tag",
            "median_reduction_pct",
        ],
    ].pivot(
        index="oil_id",
        columns="dispersion_tag",
        values="median_reduction_pct",
    )

    missing = set(SSDI_TREATMENTS) - set(comparison.columns)

    if missing:
        raise ValueError("Missing SSDI treatments: " + ", ".join(sorted(missing)))

    comparison = comparison.rename(
        columns={
            "SSDI-C9500": "c9500_reduction_pct",
            "SSDI-IBC": "ibc_reduction_pct",
        }
    ).reset_index()

    comparison["delta_pct_points"] = (
        comparison["c9500_reduction_pct"] - comparison["ibc_reduction_pct"]
    )

    return comparison.sort_values(
        "oil_id",
    ).reset_index(drop=True)


def fit_log_log_relation(
    data: pd.DataFrame,
    *,
    x: str,
    y: str = "d50_D",
) -> dict[str, float | int]:
    valid = (
        data[x].notna()
        & data[y].notna()
        & np.isfinite(data[x])
        & np.isfinite(data[y])
        & (data[x] > 0.0)
        & (data[y] > 0.0)
    )

    x_values = data.loc[
        valid,
        x,
    ].to_numpy()

    y_values = data.loc[
        valid,
        y,
    ].to_numpy()

    if len(x_values) < 2:
        raise ValueError(
            f"Not enough valid observations " f"for log-log regression: {x!r}."
        )

    log_x = np.log10(x_values)
    log_y = np.log10(y_values)

    slope, intercept = np.polyfit(
        log_x,
        log_y,
        deg=1,
    )

    predicted = intercept + slope * log_x

    ss_res = np.sum((log_y - predicted) ** 2)

    ss_tot = np.sum((log_y - np.mean(log_y)) ** 2)

    r2_log = 1.0 - ss_res / ss_tot if ss_tot > 0.0 else float("nan")

    return {
        "n": len(x_values),
        "slope": float(slope),
        "intercept": float(intercept),
        "r2_log": float(r2_log),
    }


def build_ssdi_relation_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    subsets = {
        "pooled": data,
        "ssdi_only": data.loc[data["dispersion_kind"] == "SSDI"],
    }

    records = []

    for subset_name, subset in subsets.items():
        for variable in RELATION_VARIABLES:
            records.append(
                {
                    "subset": subset_name,
                    "variable": variable,
                    **fit_log_log_relation(
                        subset,
                        x=variable,
                    ),
                }
            )

    records.append(
        {
            "subset": "pooled",
            "variable": "modified_weber",
            **fit_log_log_relation(
                data,
                x="modified_weber",
            ),
        }
    )

    return pd.DataFrame(records)


def build_ssdi_spearman_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    subsets = {
        "pooled": data,
        "ssdi_only": data.loc[data["dispersion_kind"] == "SSDI"],
    }

    records = []

    for subset_name, subset in subsets.items():
        for variable in SPEARMAN_VARIABLES:
            valid = (
                subset[variable].notna()
                & subset["d50_D"].notna()
                & np.isfinite(subset[variable])
                & np.isfinite(subset["d50_D"])
            )

            values = subset.loc[
                valid,
                [
                    variable,
                    "d50_D",
                ],
            ]

            rho = values[variable].corr(
                values["d50_D"],
                method="spearman",
            )

            records.append(
                {
                    "subset": subset_name,
                    "variable": variable,
                    "n": len(values),
                    "spearman_rho": rho,
                    "abs_spearman_rho": abs(rho),
                }
            )

    return (
        pd.DataFrame(records)
        .sort_values(
            [
                "subset",
                "abs_spearman_rho",
            ],
            ascending=[
                True,
                False,
            ],
        )
        .reset_index(drop=True)
    )
