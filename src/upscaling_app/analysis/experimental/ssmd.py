from __future__ import annotations

import pandas as pd

from upscaling_app.analysis.experimental.treatment_effect import (
    build_treatment_effects,
)


def prepare_ssmd_experimental_data(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the paired SSMD experimental dataset.

    Each SSMD experiment is paired with the corresponding untreated
    experiment through the treatment-effect preparation layer.
    """

    effects = build_treatment_effects(data)

    ssmd = effects.loc[effects["dispersion_kind"] == "SSMD"].copy()

    ssmd["dR_measured"] = ssmd["d50_ratio"]

    ssmd["water_jet_pct"] = 100.0 * ssmd["water_jet_fraction"]

    ssmd["nozzle_diameter_mm"] = (1.0e3 * ssmd["nozzle_diameter"]).round().astype(int)

    ssmd["regime"] = [
        (f"{nozzle_mm} mm — " f"{'gas' if has_gas else 'no gas'}")
        for nozzle_mm, has_gas in zip(
            ssmd["nozzle_diameter_mm"],
            ssmd["has_gas"],
        )
    ]

    return ssmd.sort_values(
        [
            "nozzle_diameter_mm",
            "has_gas",
            "oil_id",
            "water_jet_fraction",
        ]
    ).reset_index(drop=True)


def summarize_ssmd_by_regime(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize the measured SSMD response within each release regime.
    """

    return (
        data.groupby(
            "regime",
            as_index=False,
            sort=False,
        )
        .agg(
            n=(
                "experiment_id",
                "count",
            ),
            n_oils=(
                "oil_id",
                "nunique",
            ),
            mean_dR=(
                "dR_measured",
                "mean",
            ),
            std_dR=(
                "dR_measured",
                "std",
            ),
            q1_dR=(
                "dR_measured",
                lambda x: x.quantile(0.25),
            ),
            median_dR=(
                "dR_measured",
                "median",
            ),
            q3_dR=(
                "dR_measured",
                lambda x: x.quantile(0.75),
            ),
            mean_reduction_pct=(
                "d50_reduction_pct",
                "mean",
            ),
            median_reduction_pct=(
                "d50_reduction_pct",
                "median",
            ),
        )
        .reset_index(drop=True)
    )


def summarize_ssmd_by_fraction_and_regime(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize the water-jet response while keeping release regimes
    separated.
    """

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
            n=(
                "experiment_id",
                "count",
            ),
            n_oils=(
                "oil_id",
                "nunique",
            ),
            mean_dR=(
                "dR_measured",
                "mean",
            ),
            std_dR=(
                "dR_measured",
                "std",
            ),
            q1_dR=(
                "dR_measured",
                lambda x: x.quantile(0.25),
            ),
            median_dR=(
                "dR_measured",
                "median",
            ),
            q3_dR=(
                "dR_measured",
                lambda x: x.quantile(0.75),
            ),
            mean_reduction_pct=(
                "d50_reduction_pct",
                "mean",
            ),
            median_reduction_pct=(
                "d50_reduction_pct",
                "median",
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
    """
    Check whether d50 reduction increases monotonically with
    water-jet fraction for each oil within each release regime.
    """

    records = []

    for (regime, oil_id), group in data.groupby(
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
    """
    Aggregate oil-level monotonicity results by release regime.
    """

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
    """
    Pair 2 mm gas and no-gas SSMD experiments for the same oil
    and nominal water-jet fraction.

    This comparison isolates the gas/no-gas contrast while keeping
    the oil-nozzle diameter and nominal treatment level fixed.
    """

    two_mm = data.loc[data["nozzle_diameter_mm"] == 2].copy()

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
    """
    Summarize the paired 2 mm gas/no-gas comparison by
    water-jet fraction.
    """

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
            mean_dR_gas_to_no_gas=(
                "dR_gas_to_no_gas",
                "mean",
            ),
            median_delta_reduction_pct_points=(
                "delta_reduction_pct_points",
                "median",
            ),
            mean_delta_reduction_pct_points=(
                "delta_reduction_pct_points",
                "mean",
            ),
        )
        .sort_values("water_jet_fraction")
        .reset_index(drop=True)
    )


def build_ssmd_spearman_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Evaluate the monotonic association between water-jet fraction
    and measured dR within each SSMD release regime.

    The result is descriptive because observations from the same oil
    are repeated across water-jet levels.
    """

    records = []

    for regime, group in data.groupby(
        "regime",
        sort=False,
    ):
        rho = group["water_jet_fraction"].corr(
            group["dR_measured"],
            method="spearman",
        )

        records.append(
            {
                "regime": regime,
                "n": len(group),
                "n_oils": group["oil_id"].nunique(),
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
