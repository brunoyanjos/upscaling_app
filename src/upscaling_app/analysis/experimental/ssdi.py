from __future__ import annotations

import numpy as np
import pandas as pd

from upscaling_app.upscaling.ssdi.physics.derived_properties import (
    add_ssdi_physics,
)

REFERENCE_B = 0.08

RELATION_VARIABLES = [
    "weber",
    "capillary",
    "modified_weber",
]


def prepare_ssdi_experimental_data(
    data: pd.DataFrame,
    *,
    include_gas: bool = False,
) -> pd.DataFrame:
    selected = data.loc[
        data["dispersion_kind"].isin(
            [
                "Untreated",
                "SSDI",
            ]
        )
    ].copy()

    if not include_gas:
        selected = selected.loc[~selected["has_gas"]].copy()

    # Use exactly the same physical preprocessing
    # as the validated SSDI model.
    selected = add_ssdi_physics(selected)

    selected["d50_D"] = selected["measured_d50"] / selected["nozzle_diameter"]

    selected["modified_weber"] = selected["weber"] / (
        1.0 + REFERENCE_B * selected["capillary"] * selected["d50_D"] ** (1.0 / 3.0)
    )

    return selected.reset_index(drop=True)


def fit_log_log_relation(
    data: pd.DataFrame,
    *,
    x: str,
    y: str = "d50_D",
) -> dict[str, float]:
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
            f"Not enough valid observations " f"for log-log regression: {x}"
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

    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0.0 else float("nan")

    return {
        "n": len(x_values),
        "slope": float(slope),
        "intercept": float(intercept),
        "r2_log": float(r2),
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
            metrics = fit_log_log_relation(
                subset,
                x=variable,
            )

            records.append(
                {
                    "subset": subset_name,
                    "variable": variable,
                    **metrics,
                }
            )

    return pd.DataFrame(records)


SSDI_SPEARMAN_VARIABLES = [
    "volumetric_velocity",
    "modified_velocity",
    "effective_velocity",
    "froude",
    "reynolds",
    "weber",
    "capillary",
]


def build_ssdi_spearman_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    analysis_data = data.copy()

    records = []

    for variable in SSDI_SPEARMAN_VARIABLES:
        valid = (
            analysis_data[variable].notna()
            & analysis_data["d50_D"].notna()
            & np.isfinite(analysis_data[variable])
            & np.isfinite(analysis_data["d50_D"])
        )

        subset = analysis_data.loc[
            valid,
            [variable, "d50_D"],
        ]

        rho = subset[variable].corr(
            subset["d50_D"],
            method="spearman",
        )

        records.append(
            {
                "variable": variable,
                "n": len(subset),
                "spearman_rho": rho,
                "abs_spearman_rho": abs(rho),
            }
        )

    return (
        pd.DataFrame(records)
        .sort_values(
            "abs_spearman_rho",
            ascending=False,
        )
        .reset_index(drop=True)
    )
