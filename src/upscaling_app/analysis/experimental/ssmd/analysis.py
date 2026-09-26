from __future__ import annotations

import numpy as np
import pandas as pd

from upscaling_app.upscaling.ssmd.physics.derived_properties import (
    add_derived_properties,
)

PAIR_KEYS = (
    "oil_id",
    "nozzle_diameter",
    "has_gas",
)


def prepare_ssmd_experimental_data(
    data: pd.DataFrame,
) -> pd.DataFrame:
    ssmd = data.loc[data["dispersion_kind"] == "SSMD"].copy()

    untreated_columns = [
        *PAIR_KEYS,
        "measured_d50",
        "ift",
        "oil_flow",
        "gas_flow",
        "oil_density",
        "gas_density",
    ]

    untreated = (
        data.loc[
            data["dispersion_kind"] == "Untreated",
            untreated_columns,
        ]
        .rename(
            columns={
                "measured_d50": "untreated_d50_measured",
                "ift": "untreated_ift",
                "oil_flow": "untreated_oil_flow",
                "gas_flow": "untreated_gas_flow",
                "oil_density": "untreated_oil_density",
                "gas_density": "untreated_gas_density",
            }
        )
        .copy()
    )

    if untreated.duplicated(
        subset=list(PAIR_KEYS),
        keep=False,
    ).any():
        raise ValueError(
            "Multiple untreated references found for the same "
            "oil, nozzle diameter and gas condition."
        )

    ssmd = ssmd.merge(
        untreated,
        on=list(PAIR_KEYS),
        how="left",
        validate="many_to_one",
    )

    required = [
        "untreated_d50_measured",
        "untreated_ift",
        "untreated_oil_flow",
        "untreated_gas_flow",
        "untreated_oil_density",
        "untreated_gas_density",
    ]

    missing = ssmd[required].isna().sum()
    missing = missing.loc[missing > 0]

    if not missing.empty:
        raise ValueError(
            "Missing untreated SSMD reference data:\n" f"{missing.to_string()}"
        )

    ssmd = add_derived_properties(ssmd)

    ssmd["d50_ratio"] = ssmd["dR_measured"]

    ssmd["d50_reduction"] = ssmd["untreated_d50_measured"] - ssmd["measured_d50"]

    ssmd["d50_reduction_pct"] = 100.0 * (1.0 - ssmd["dR_measured"])

    ssmd["water_jet_pct"] = 100.0 * ssmd["water_jet_fraction"]

    nozzle_diameter_mm = (1.0e3 * ssmd["nozzle_diameter"]).round().astype(int)

    ssmd["regime"] = [
        (f"{diameter} mm — " f"{'gas' if has_gas else 'no gas'}")
        for diameter, has_gas in zip(
            nozzle_diameter_mm,
            ssmd["has_gas"],
        )
    ]

    return ssmd.sort_values(
        [
            "nozzle_diameter",
            "has_gas",
            "oil_id",
            "water_jet_fraction",
        ]
    ).reset_index(drop=True)


def summarize_ssmd_by_regime(
    data: pd.DataFrame,
) -> pd.DataFrame:
    return (
        data.groupby(
            "regime",
            as_index=False,
            sort=False,
        )
        .agg(
            n_experiments=(
                "experiment_id",
                "count",
            ),
            n_oils=(
                "oil_id",
                "nunique",
            ),
            median_dR=(
                "dR_measured",
                "median",
            ),
            q1_reduction_pct=(
                "d50_reduction_pct",
                lambda values: values.quantile(0.25),
            ),
            median_reduction_pct=(
                "d50_reduction_pct",
                "median",
            ),
            q3_reduction_pct=(
                "d50_reduction_pct",
                lambda values: values.quantile(0.75),
            ),
        )
        .reset_index(drop=True)
    )


def summarize_ssmd_by_fraction_and_regime(
    data: pd.DataFrame,
) -> pd.DataFrame:
    return (
        data.groupby(
            [
                "regime",
                "water_jet_fraction",
                "water_jet_pct",
            ],
            as_index=False,
            sort=False,
        )
        .agg(
            n_experiments=(
                "experiment_id",
                "count",
            ),
            n_oils=(
                "oil_id",
                "nunique",
            ),
            median_dR=(
                "dR_measured",
                "median",
            ),
            q1_reduction_pct=(
                "d50_reduction_pct",
                lambda values: values.quantile(0.25),
            ),
            median_reduction_pct=(
                "d50_reduction_pct",
                "median",
            ),
            q3_reduction_pct=(
                "d50_reduction_pct",
                lambda values: values.quantile(0.75),
            ),
        )
        .sort_values(
            [
                "regime",
                "water_jet_fraction",
            ]
        )
        .reset_index(drop=True)
    )


def summarize_ssmd_monotonicity(
    data: pd.DataFrame,
) -> pd.DataFrame:
    records = []

    for (
        regime,
        oil_id,
    ), group in data.groupby(
        [
            "regime",
            "oil_id",
        ],
        sort=False,
    ):
        ordered = group.sort_values("water_jet_fraction")

        reduction = ordered["d50_reduction_pct"]

        records.append(
            {
                "regime": regime,
                "oil_id": oil_id,
                "n_levels": len(ordered),
                "is_monotonic": (reduction.is_monotonic_increasing),
                "first_reduction_pct": (reduction.iloc[0]),
                "last_reduction_pct": (reduction.iloc[-1]),
                "delta_pct_points": (reduction.iloc[-1] - reduction.iloc[0]),
            }
        )

    return (
        pd.DataFrame(records)
        .sort_values(
            [
                "regime",
                "oil_id",
            ]
        )
        .reset_index(drop=True)
    )


def summarize_ssmd_monotonicity_by_regime(
    monotonicity: pd.DataFrame,
) -> pd.DataFrame:
    summary = monotonicity.groupby(
        "regime",
        as_index=False,
        sort=False,
    ).agg(
        n_oils=(
            "oil_id",
            "nunique",
        ),
        n_monotonic=(
            "is_monotonic",
            "sum",
        ),
    )

    summary["monotonic_fraction"] = summary["n_monotonic"] / summary["n_oils"]

    return summary.reset_index(drop=True)


def build_ssmd_gas_comparison(
    data: pd.DataFrame,
) -> pd.DataFrame:
    two_mm = data.loc[
        np.isclose(
            data["nozzle_diameter"],
            0.002,
        )
    ].copy()

    no_gas = two_mm.loc[
        ~two_mm["has_gas"],
        [
            "oil_id",
            "water_jet_fraction",
            "water_jet_pct",
            "dR_measured",
            "d50_reduction_pct",
        ],
    ].rename(
        columns={
            "dR_measured": "dR_no_gas",
            "d50_reduction_pct": ("reduction_no_gas_pct"),
        }
    )

    gas = two_mm.loc[
        two_mm["has_gas"],
        [
            "oil_id",
            "water_jet_fraction",
            "dR_measured",
            "d50_reduction_pct",
        ],
    ].rename(
        columns={
            "dR_measured": "dR_gas",
            "d50_reduction_pct": ("reduction_gas_pct"),
        }
    )

    comparison = no_gas.merge(
        gas,
        on=[
            "oil_id",
            "water_jet_fraction",
        ],
        how="inner",
        validate="one_to_one",
    )

    comparison["dR_gas_to_no_gas"] = comparison["dR_gas"] / comparison["dR_no_gas"]

    comparison["delta_reduction_pct_points"] = (
        comparison["reduction_gas_pct"] - comparison["reduction_no_gas_pct"]
    )

    return comparison.sort_values(
        [
            "oil_id",
            "water_jet_fraction",
        ]
    ).reset_index(drop=True)


def summarize_ssmd_gas_comparison(
    comparison: pd.DataFrame,
) -> pd.DataFrame:
    return (
        comparison.groupby(
            [
                "water_jet_fraction",
                "water_jet_pct",
            ],
            as_index=False,
        )
        .agg(
            n_pairs=(
                "oil_id",
                "count",
            ),
            median_dR_gas_to_no_gas=(
                "dR_gas_to_no_gas",
                "median",
            ),
            q1_dR_gas_to_no_gas=(
                "dR_gas_to_no_gas",
                lambda values: values.quantile(0.25),
            ),
            q3_dR_gas_to_no_gas=(
                "dR_gas_to_no_gas",
                lambda values: values.quantile(0.75),
            ),
            median_delta_reduction_pct_points=(
                "delta_reduction_pct_points",
                "median",
            ),
        )
        .sort_values("water_jet_fraction")
        .reset_index(drop=True)
    )


def fit_log_log_relation(
    data: pd.DataFrame,
    *,
    x: str,
    y: str,
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
            f"Not enough valid observations for " f"log-log regression: {x!r} vs {y!r}."
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


def build_ssmd_momentum_relation_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    records = [
        {
            "regime": "global",
            **fit_log_log_relation(
                data,
                x="momentum_amplification",
                y="dR_measured",
            ),
        }
    ]

    for regime, group in data.groupby(
        "regime",
        sort=False,
    ):
        records.append(
            {
                "regime": regime,
                **fit_log_log_relation(
                    group,
                    x="momentum_amplification",
                    y="dR_measured",
                ),
            }
        )

    return pd.DataFrame(records)
