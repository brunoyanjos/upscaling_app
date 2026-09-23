from __future__ import annotations

import pandas as pd

NUMERIC_VARIABLES = [
    "nozzle_diameter",
    "ift",
    "oil_flow",
    "gas_flow",
    "water_jet_fraction",
    "water_flow",
    "water_nozzle_diameter",
    "oil_viscosity",
    "gas_density",
    "oil_density",
    "measured_d50",
]


def summarize_dataset(
    data: pd.DataFrame,
) -> dict[str, object]:
    return {
        "n_experiments": len(data),
        "n_oils": data["oil_id"].nunique(),
        "dispersion_counts": (data["dispersion_kind"].value_counts().sort_index()),
        "gas_counts": (data["has_gas"].value_counts().sort_index()),
        "nozzle_counts": (data["nozzle_diameter"].value_counts().sort_index()),
    }


def summarize_variable(
    data: pd.DataFrame,
    variable: str,
) -> pd.Series:
    values = data[variable].dropna()

    if values.empty:
        return pd.Series(
            {
                "count": 0,
                "mean": float("nan"),
                "std": float("nan"),
                "cv": float("nan"),
                "min": float("nan"),
                "q1": float("nan"),
                "median": float("nan"),
                "q3": float("nan"),
                "max": float("nan"),
            },
            name=variable,
        )

    mean = values.mean()
    std = values.std()

    return pd.Series(
        {
            "count": values.count(),
            "mean": mean,
            "std": std,
            "cv": std / mean if mean != 0 else float("nan"),
            "min": values.min(),
            "q1": values.quantile(0.25),
            "median": values.median(),
            "q3": values.quantile(0.75),
            "max": values.max(),
        },
        name=variable,
    )


def summarize_variables(
    data: pd.DataFrame,
) -> pd.DataFrame:
    available_variables = [
        variable for variable in NUMERIC_VARIABLES if variable in data.columns
    ]

    summaries = [summarize_variable(data, variable) for variable in available_variables]

    return pd.DataFrame(summaries)


def summarize_by_oil(
    data: pd.DataFrame,
    variable: str = "measured_d50",
) -> pd.DataFrame:
    return (
        data.groupby(
            "oil_id",
            dropna=False,
        )[variable]
        .agg(
            count="count",
            mean="mean",
            std="std",
            min="min",
            median="median",
            max="max",
        )
        .reset_index()
    )


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
            n_experiments=("experiment_id", "count"),
            n_oils=("oil_id", "nunique"),
            d50_mean=("measured_d50", "mean"),
            d50_std=("measured_d50", "std"),
            d50_median=("measured_d50", "median"),
            d50_min=("measured_d50", "min"),
            d50_max=("measured_d50", "max"),
        )
        .reset_index()
    )


def correlation_matrix(
    data: pd.DataFrame,
    method: str = "pearson",
) -> pd.DataFrame:
    available_variables = [
        variable
        for variable in NUMERIC_VARIABLES
        if variable in data.columns and data[variable].notna().any()
    ]

    return data[available_variables].corr(
        method=method,
    )
