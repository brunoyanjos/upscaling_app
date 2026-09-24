from __future__ import annotations

import pandas as pd

from upscaling_app.upscaling.ssmd.physics.derived_properties import (
    add_derived_properties,
)

# ============================================================
# Data preparation
# ============================================================


def prepare_ssmd_experimental_data(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the paired SSMD experimental dataset using the same
    physical preprocessing as the production SSMD pipeline.
    """

    ssmd = data.loc[data["dispersion_kind"] == "SSMD"].copy()

    untreated_columns = [
        "oil_id",
        "nozzle_diameter",
        "has_gas",
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

    ssmd = ssmd.merge(
        untreated,
        on=[
            "oil_id",
            "nozzle_diameter",
            "has_gas",
        ],
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

    if ssmd[required].isna().any().any():
        missing = ssmd[required].isna().sum()

        missing = missing.loc[missing > 0]

        raise ValueError(
            "Missing untreated SSMD reference data:\n" f"{missing.to_string()}"
        )

    # Same preprocessing used by the SSMD production model.
    ssmd = add_derived_properties(ssmd)

    ssmd["d50_ratio"] = ssmd["dR_measured"]

    ssmd["d50_reduction"] = ssmd["untreated_d50_measured"] - ssmd["measured_d50"]

    ssmd["d50_reduction_pct"] = 100.0 * (1.0 - ssmd["dR_measured"])

    ssmd["water_jet_pct"] = 100.0 * ssmd["water_jet_fraction"]

    ssmd["nozzle_diameter_mm"] = (1.0e3 * ssmd["nozzle_diameter"]).round().astype(int)

    ssmd["regime"] = [
        (f"{nozzle_mm} mm — " f"{'gas' if has_gas else 'no gas'}")
        for nozzle_mm, has_gas in zip(
            ssmd["nozzle_diameter_mm"],
            ssmd["has_gas"],
        )
    ]

    ssmd["viscosity_ift_ratio"] = ssmd["oil_viscosity"] / ssmd["untreated_ift"]

    ssmd["reference_eta"] = ssmd["has_gas"].map(
        {
            False: 0.85,
            True: 0.6779545878291601,
        }
    )

    ssmd["hydrodynamic_dR"] = (
        ssmd["reference_eta"] * ssmd["momentum_amplification"]
    ) ** (-3.0 / 5.0)

    ssmd["property_correction_ratio"] = ssmd["dR_measured"] / ssmd["hydrodynamic_dR"]

    return ssmd.sort_values(
        [
            "nozzle_diameter_mm",
            "has_gas",
            "oil_id",
            "water_jet_fraction",
        ]
    ).reset_index(drop=True)


# ============================================================
# Descriptive summaries
# ============================================================


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
            q1_reduction_pct=(
                "d50_reduction_pct",
                lambda x: x.quantile(0.25),
            ),
            median_reduction_pct=(
                "d50_reduction_pct",
                "median",
            ),
            q3_reduction_pct=(
                "d50_reduction_pct",
                lambda x: x.quantile(0.75),
            ),
            mean_reduction_pct=(
                "d50_reduction_pct",
                "mean",
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


# ============================================================
# Water-jet screening
# ============================================================


def build_ssmd_spearman_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
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


# ============================================================
# SINTEF physical screening
# ============================================================


def build_ssmd_hydrodynamic_spearman_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Screen the experimental dR response against SINTEF momentum
    amplification within each release regime.
    """

    records = []

    for regime, group in data.groupby(
        "regime",
        sort=False,
    ):
        rho = group["momentum_amplification"].corr(
            group["dR_measured"],
            method="spearman",
        )

        records.append(
            {
                "regime": regime,
                "variable": "momentum_amplification",
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


def build_ssmd_property_spearman_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Screen oil-property associations with dR.

    One representative value per oil and regime is used to avoid
    treating the three water-jet levels as independent oil-property
    observations.
    """

    variables = [
        "oil_viscosity",
        "untreated_ift",
        "viscosity_ift_ratio",
    ]

    oil_summary = data.groupby(
        [
            "regime",
            "oil_id",
        ],
        as_index=False,
        sort=False,
    ).agg(
        dR_measured=(
            "dR_measured",
            "median",
        ),
        oil_viscosity=(
            "oil_viscosity",
            "median",
        ),
        untreated_ift=(
            "untreated_ift",
            "median",
        ),
        viscosity_ift_ratio=(
            "viscosity_ift_ratio",
            "median",
        ),
    )

    records = []

    for regime, group in oil_summary.groupby(
        "regime",
        sort=False,
    ):
        for variable in variables:
            rho = group[variable].corr(
                group["dR_measured"],
                method="spearman",
            )

            records.append(
                {
                    "regime": regime,
                    "variable": variable,
                    "n_oils": len(group),
                    "spearman_rho": rho,
                    "abs_spearman_rho": abs(rho),
                }
            )

    return (
        pd.DataFrame(records)
        .sort_values(
            [
                "regime",
                "abs_spearman_rho",
            ],
            ascending=[
                True,
                False,
            ],
        )
        .reset_index(drop=True)
    )


def build_ssmd_property_correction_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Evaluate the oil-property structure remaining after removing the
    reference SINTEF Equation-5 hydrodynamic contribution.

    Equation 6 suggests:

        dR / (eta * A_M)^(-3/5)
            ~ c + d * mu / sigma
    """

    oil_summary = data.groupby(
        [
            "regime",
            "oil_id",
        ],
        as_index=False,
        sort=False,
    ).agg(
        property_correction_ratio=(
            "property_correction_ratio",
            "median",
        ),
        viscosity_ift_ratio=(
            "viscosity_ift_ratio",
            "median",
        ),
    )

    records = []

    for regime, group in oil_summary.groupby(
        "regime",
        sort=False,
    ):
        rho = group["viscosity_ift_ratio"].corr(
            group["property_correction_ratio"],
            method="spearman",
        )

        records.append(
            {
                "regime": regime,
                "n_oils": len(group),
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


# ============================================================
# Monotonicity
# ============================================================


def summarize_ssmd_monotonicity(
    data: pd.DataFrame,
) -> pd.DataFrame:
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


# ============================================================
# Gas / no-gas comparison
# ============================================================


def build_ssmd_gas_comparison(
    data: pd.DataFrame,
) -> pd.DataFrame:
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
