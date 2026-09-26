from __future__ import annotations

from typing import Final

import pandas as pd

PAIR_KEYS: Final[tuple[str, ...]] = (
    "oil_id",
    "nozzle_diameter",
    "has_gas",
)


def build_treatment_effects(
    data: pd.DataFrame,
) -> pd.DataFrame:
    untreated = (
        data.loc[
            data["dispersion_kind"] == "Untreated",
            [*PAIR_KEYS, "measured_d50"],
        ]
        .rename(
            columns={
                "measured_d50": "untreated_d50",
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

    treated = data.loc[data["dispersion_kind"] != "Untreated"].copy()

    effects = treated.merge(
        untreated,
        on=list(PAIR_KEYS),
        how="left",
        validate="many_to_one",
    )

    if effects["untreated_d50"].isna().any():
        raise ValueError(
            "Some treated experiments could not be paired "
            "with an untreated reference."
        )

    effects["d50_ratio"] = effects["measured_d50"] / effects["untreated_d50"]

    effects["d50_reduction"] = effects["untreated_d50"] - effects["measured_d50"]

    effects["d50_reduction_pct"] = 100.0 * (1.0 - effects["d50_ratio"])

    return effects.reset_index(drop=True)


def summarize_treatment_by_oil(
    effects: pd.DataFrame,
) -> pd.DataFrame:
    return (
        effects.groupby(
            [
                "oil_id",
                "dispersion_tag",
            ],
            as_index=False,
        )
        .agg(
            n_experiments=(
                "experiment_id",
                "count",
            ),
            median_reduction_pct=(
                "d50_reduction_pct",
                "median",
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
                "dispersion_tag",
                "oil_id",
            ]
        )
        .reset_index(drop=True)
    )


def summarize_treatment_by_method(
    by_oil: pd.DataFrame,
) -> pd.DataFrame:
    return (
        by_oil.groupby(
            "dispersion_tag",
            as_index=False,
        )
        .agg(
            n_experiments=(
                "n_experiments",
                "sum",
            ),
            n_oils=(
                "oil_id",
                "nunique",
            ),
            median_reduction_pct=(
                "median_reduction_pct",
                "median",
            ),
            q1_reduction_pct=(
                "median_reduction_pct",
                lambda values: values.quantile(0.25),
            ),
            q3_reduction_pct=(
                "median_reduction_pct",
                lambda values: values.quantile(0.75),
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
        .reset_index(drop=True)
    )
