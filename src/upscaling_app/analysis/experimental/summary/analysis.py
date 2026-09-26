from __future__ import annotations

from typing import Final

import pandas as pd

CORE_FIELDS: Final[tuple[str, ...]] = (
    "experiment_id",
    "oil_id",
    "dispersion_kind",
    "dispersion_tag",
    "nozzle_diameter",
    "has_gas",
    "measured_d50",
    "source_sheet",
)

TREATMENT_ORDER = (
    "Untreated",
    "SSDI-C9500",
    "SSDI-IBC",
    "WJ-40%",
    "WJ-45%",
    "WJ-50%",
    "WJ-55%",
)


DISPERSION_KINDS: Final[tuple[str, ...]] = (
    "Untreated",
    "SSDI",
    "SSMD",
)


def summarize_dataset(
    data: pd.DataFrame,
) -> dict[str, int]:
    counts = data["dispersion_kind"].value_counts()

    return {
        "n_rows": len(data),
        "n_experiments": data["experiment_id"].nunique(),
        "n_oils": data["oil_id"].nunique(),
        "n_duplicate_experiment_ids": data["experiment_id"].duplicated().sum(),
        "n_untreated": int(counts.get("Untreated", 0)),
        "n_ssdi": int(counts.get("SSDI", 0)),
        "n_ssmd": int(counts.get("SSMD", 0)),
    }


def summarize_regimes(
    data: pd.DataFrame,
) -> pd.DataFrame:
    return (
        data.groupby(
            [
                "dispersion_kind",
                "nozzle_diameter",
                "has_gas",
            ],
            dropna=False,
        )
        .agg(
            n_experiments=("experiment_id", "nunique"),
            n_oils=("oil_id", "nunique"),
        )
        .reset_index()
        .sort_values(
            [
                "dispersion_kind",
                "nozzle_diameter",
                "has_gas",
            ]
        )
        .reset_index(drop=True)
    )


def summarize_oil_coverage(
    data: pd.DataFrame,
) -> pd.DataFrame:
    coverage = pd.crosstab(
        data["oil_id"],
        data["dispersion_kind"],
    )

    coverage = coverage.reindex(
        columns=DISPERSION_KINDS,
        fill_value=0,
    )

    coverage = coverage.rename(
        columns={
            "Untreated": "n_untreated",
            "SSDI": "n_ssdi",
            "SSMD": "n_ssmd",
        }
    )

    coverage.insert(
        0,
        "n_experiments",
        coverage.sum(axis=1),
    )

    return coverage.reset_index()


def summarize_completeness(
    data: pd.DataFrame,
) -> pd.DataFrame:
    fields = [field for field in CORE_FIELDS if field in data.columns]

    rows = []

    for field in fields:
        n_present = int(data[field].notna().sum())
        n_missing = int(data[field].isna().sum())

        rows.append(
            {
                "field": field,
                "n_present": n_present,
                "n_missing": n_missing,
                "completeness_pct": 100.0 * n_present / len(data),
            }
        )

    return pd.DataFrame(rows)


def summarize_oil_treatment_coverage(
    data: pd.DataFrame,
) -> pd.DataFrame:
    treatment = data["dispersion_tag"].where(
        data["dispersion_kind"] != "Untreated",
        "Untreated",
    )

    coverage = pd.crosstab(
        data["oil_id"],
        treatment,
    )

    available = [
        treatment for treatment in TREATMENT_ORDER if treatment in coverage.columns
    ]

    extra = [
        treatment for treatment in coverage.columns if treatment not in TREATMENT_ORDER
    ]

    coverage = coverage.reindex(
        columns=[*available, *extra],
        fill_value=0,
    )

    return coverage.reset_index()
