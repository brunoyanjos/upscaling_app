from __future__ import annotations

import pandas as pd

PAIR_KEYS = [
    "oil_id",
    "nozzle_diameter",
    "has_gas",
]


def build_treatment_effects(
    data: pd.DataFrame,
) -> pd.DataFrame:
    untreated = (
        data.loc[
            data["dispersion_kind"] == "Untreated",
            PAIR_KEYS + ["measured_d50"],
        ]
        .rename(
            columns={
                "measured_d50": "untreated_d50",
            }
        )
        .copy()
    )

    treated = data.loc[data["dispersion_kind"] != "Untreated"].copy()

    result = treated.merge(
        untreated,
        on=PAIR_KEYS,
        how="left",
        validate="many_to_one",
    )

    if result["untreated_d50"].isna().any():
        raise ValueError(
            "Some treated experiments could not be paired "
            "with an untreated reference."
        )

    result["d50_ratio"] = result["measured_d50"] / result["untreated_d50"]

    result["d50_reduction"] = result["untreated_d50"] - result["measured_d50"]

    result["d50_reduction_pct"] = 100.0 * (1.0 - result["d50_ratio"])

    return result.reset_index(drop=True)


def summarize_treatment_effect_by_oil(
    effects: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        effects.groupby(
            [
                "oil_id",
                "dispersion_tag",
            ],
            as_index=False,
        )
        .agg(
            n=(
                "experiment_id",
                "count",
            ),
            median_reduction_pct=(
                "d50_reduction_pct",
                "median",
            ),
            mean_reduction_pct=(
                "d50_reduction_pct",
                "mean",
            ),
            min_reduction_pct=(
                "d50_reduction_pct",
                "min",
            ),
            max_reduction_pct=(
                "d50_reduction_pct",
                "max",
            ),
        )
        .sort_values(
            [
                "oil_id",
                "dispersion_tag",
            ]
        )
        .reset_index(drop=True)
    )

    return summary


def summarize_treatment_by_method(
    summary: pd.DataFrame,
) -> pd.DataFrame:
    by_method = (
        summary.groupby(
            "dispersion_tag",
            as_index=False,
        )
        .agg(
            n_oils=(
                "oil_id",
                "nunique",
            ),
            median_reduction_pct=(
                "median_reduction_pct",
                "median",
            ),
            mean_reduction_pct=(
                "median_reduction_pct",
                "mean",
            ),
            min_reduction_pct=(
                "median_reduction_pct",
                "min",
            ),
            max_reduction_pct=(
                "median_reduction_pct",
                "max",
            ),
        )
        .sort_values(
            "median_reduction_pct",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return by_method


def rank_treatment_effects(
    summary: pd.DataFrame,
    n: int = 5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    ranked = summary.sort_values(
        "median_reduction_pct",
        ascending=False,
    )

    best = ranked.head(n).reset_index(drop=True)

    worst = (
        ranked.tail(n)
        .sort_values(
            "median_reduction_pct",
            ascending=True,
        )
        .reset_index(drop=True)
    )

    return best, worst


def flag_treatment_outliers(
    summary: pd.DataFrame,
) -> pd.DataFrame:
    result = summary.copy()

    result["is_outlier"] = False

    for treatment, group in result.groupby("dispersion_tag"):
        q1 = group["median_reduction_pct"].quantile(0.25)

        q3 = group["median_reduction_pct"].quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        mask = (result["dispersion_tag"] == treatment) & (
            (result["median_reduction_pct"] < lower)
            | (result["median_reduction_pct"] > upper)
        )

        result.loc[
            mask,
            "is_outlier",
        ] = True

    return result


def build_outlier_diagnostics(
    effects: pd.DataFrame,
    flagged: pd.DataFrame,
) -> pd.DataFrame:
    outliers = flagged.loc[flagged["is_outlier"]][
        [
            "oil_id",
            "dispersion_tag",
        ]
    ]

    diagnostics = effects.merge(
        outliers,
        on=[
            "oil_id",
            "dispersion_tag",
        ],
        how="inner",
    )

    return diagnostics[
        [
            "oil_id",
            "dispersion_tag",
            "nozzle_diameter",
            "has_gas",
            "water_jet_fraction",
            "measured_d50",
            "untreated_d50",
            "d50_ratio",
            "d50_reduction_pct",
        ]
    ].sort_values(
        [
            "dispersion_tag",
            "oil_id",
        ]
    )


def summarize_water_jet_response(
    effects: pd.DataFrame,
) -> pd.DataFrame:
    ssmd = effects.loc[effects["dispersion_kind"] == "SSMD"].copy()

    by_oil = ssmd.groupby(
        [
            "oil_id",
            "water_jet_fraction",
        ],
        as_index=False,
    ).agg(
        n=(
            "experiment_id",
            "count",
        ),
        median_reduction_pct=(
            "d50_reduction_pct",
            "median",
        ),
        mean_reduction_pct=(
            "d50_reduction_pct",
            "mean",
        ),
        min_reduction_pct=(
            "d50_reduction_pct",
            "min",
        ),
        max_reduction_pct=(
            "d50_reduction_pct",
            "max",
        ),
    )

    by_oil["water_jet_pct"] = 100.0 * by_oil["water_jet_fraction"]

    return by_oil.sort_values(
        [
            "oil_id",
            "water_jet_fraction",
        ]
    ).reset_index(drop=True)


def summarize_water_jet_by_fraction(
    by_oil: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        by_oil.groupby(
            [
                "water_jet_fraction",
                "water_jet_pct",
            ],
            as_index=False,
        )
        .agg(
            n_oils=(
                "oil_id",
                "nunique",
            ),
            median_reduction_pct=(
                "median_reduction_pct",
                "median",
            ),
            mean_reduction_pct=(
                "median_reduction_pct",
                "mean",
            ),
            min_reduction_pct=(
                "median_reduction_pct",
                "min",
            ),
            max_reduction_pct=(
                "median_reduction_pct",
                "max",
            ),
        )
        .sort_values("water_jet_fraction")
        .reset_index(drop=True)
    )

    return summary


def summarize_water_jet_monotonicity(
    by_oil: pd.DataFrame,
) -> pd.DataFrame:
    records = []

    for oil_id, group in by_oil.groupby("oil_id"):
        ordered = group.sort_values("water_jet_fraction")

        reduction = ordered["median_reduction_pct"]

        records.append(
            {
                "oil_id": oil_id,
                "n_levels": len(ordered),
                "is_monotonic": (reduction.is_monotonic_increasing),
                "first_reduction_pct": (reduction.iloc[0]),
                "last_reduction_pct": (reduction.iloc[-1]),
                "delta_pct_points": (reduction.iloc[-1] - reduction.iloc[0]),
            }
        )

    return pd.DataFrame(records).sort_values("oil_id").reset_index(drop=True)


def build_ssdi_dispersant_comparison(
    by_oil: pd.DataFrame,
) -> pd.DataFrame:
    tags = [
        "SSDI-C9500",
        "SSDI-IBC",
    ]

    ssdi = by_oil.loc[
        by_oil["dispersion_tag"].isin(tags),
        [
            "oil_id",
            "dispersion_tag",
            "median_reduction_pct",
        ],
    ].copy()

    comparison = ssdi.pivot(
        index="oil_id",
        columns="dispersion_tag",
        values="median_reduction_pct",
    )

    missing = set(tags) - set(comparison.columns)

    if missing:
        raise ValueError("Missing SSDI treatments: " + ", ".join(sorted(missing)))

    comparison = comparison.rename(
        columns={
            "SSDI-C9500": ("c9500_reduction_pct"),
            "SSDI-IBC": ("ibc_reduction_pct"),
        }
    ).reset_index()

    comparison["delta_pct_points"] = (
        comparison["c9500_reduction_pct"] - comparison["ibc_reduction_pct"]
    )

    comparison["c9500_higher_reduction"] = comparison["delta_pct_points"] > 0.0

    return comparison.sort_values(
        "delta_pct_points",
        ascending=False,
    ).reset_index(drop=True)
