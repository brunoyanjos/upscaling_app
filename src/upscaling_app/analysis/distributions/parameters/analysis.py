import numpy as np
import pandas as pd

from upscaling_app.analysis.distributions.analysis import (
    add_distribution_regime,
)
from upscaling_app.upscaling.distributions.rosin_rammler import (
    rosin_rammler_quantile,
)

PARAMETER_COLUMNS = [
    "cdf_shape",
    "cdf_scale",
]

FIT_QUALITY_COLUMNS = [
    "cdf_rmse",
    "cdf_max_error",
    "cdf_mass_rmse",
    "cdf_mass_max_error",
    "cdf_total_variation",
]


def prepare_distribution_parameter_data(
    parameters: pd.DataFrame,
    experiments: pd.DataFrame,
) -> pd.DataFrame:
    required_parameter_columns = [
        "experiment_id",
        *PARAMETER_COLUMNS,
    ]

    missing_parameters = [
        column
        for column in required_parameter_columns
        if column not in parameters.columns
    ]

    if missing_parameters:
        raise ValueError("Missing parameter columns: " + ", ".join(missing_parameters))

    experiment_columns = [
        "experiment_id",
        "oil_id",
        "dispersion_kind",
        "dispersion_tag",
        "nozzle_diameter",
        "has_gas",
        "water_jet_fraction",
        "measured_d50",
    ]

    missing_experiments = [
        column for column in experiment_columns if column not in experiments.columns
    ]

    if missing_experiments:
        raise ValueError(
            "Missing experiment columns: " + ", ".join(missing_experiments)
        )

    if parameters["experiment_id"].duplicated().any():
        raise ValueError("parameters contains duplicated experiment_id values.")

    if experiments["experiment_id"].duplicated().any():
        raise ValueError("experiments contains duplicated experiment_id values.")

    data = experiments[experiment_columns].merge(
        parameters[required_parameter_columns],
        on="experiment_id",
        how="inner",
        validate="one_to_one",
    )

    if len(data) != len(parameters):
        raise ValueError(
            "Not all fitted parameter sets could be matched "
            "to experimental metadata."
        )

    data = data.rename(
        columns={
            "cdf_shape": "shape",
            "cdf_scale": "scale",
        }
    )

    data = add_distribution_regime(data)

    data["rr_d50"] = rosin_rammler_quantile(
        quantile=0.5,
        shape=data["shape"].to_numpy(dtype=float),
        scale=data["scale"].to_numpy(dtype=float),
    )

    data["scale_to_rr_d50"] = data["scale"] / data["rr_d50"]

    return data.sort_values(
        [
            "distribution_regime",
            "oil_id",
            "experiment_id",
        ]
    ).reset_index(drop=True)


def _summarize_parameter(
    values: np.ndarray,
) -> dict[str, float]:
    values = np.asarray(
        values,
        dtype=float,
    )

    values = values[np.isfinite(values)]

    if values.size == 0:
        raise ValueError("No finite parameter values available.")

    return {
        "n": int(values.size),
        "mean": float(np.mean(values)),
        "std": float(
            np.std(
                values,
                ddof=1,
            )
        ),
        "min": float(np.min(values)),
        "q25": float(
            np.quantile(
                values,
                0.25,
            )
        ),
        "median": float(np.median(values)),
        "q75": float(
            np.quantile(
                values,
                0.75,
            )
        ),
        "max": float(np.max(values)),
    }


def summarize_distribution_parameters(
    data: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    parameter_columns = {
        "shape": "shape",
        "scale": "scale",
        "rr_d50": "rr_d50",
        "scale_to_rr_d50": ("scale_to_rr_d50"),
    }

    for (
        parameter,
        column,
    ) in parameter_columns.items():
        summary = _summarize_parameter(data[column].to_numpy(dtype=float))

        rows.append(
            {
                "regime": "All",
                "parameter": parameter,
                **summary,
            }
        )

    for (
        regime,
        subset,
    ) in data.groupby(
        "distribution_regime",
        sort=False,
    ):
        for (
            parameter,
            column,
        ) in parameter_columns.items():
            summary = _summarize_parameter(subset[column].to_numpy(dtype=float))

            rows.append(
                {
                    "regime": regime,
                    "parameter": parameter,
                    **summary,
                }
            )

    return pd.DataFrame(rows)


def attach_distribution_fit_quality(
    data: pd.DataFrame,
    evaluation: pd.DataFrame,
) -> pd.DataFrame:
    required_columns = [
        "experiment_id",
        *FIT_QUALITY_COLUMNS,
    ]

    missing = [
        column for column in required_columns if column not in evaluation.columns
    ]

    if missing:
        raise ValueError("Missing fit-quality columns: " + ", ".join(missing))

    quality = evaluation[required_columns].copy()

    if quality["experiment_id"].duplicated().any():
        raise ValueError("Fit evaluation contains duplicated " "experiment_id values.")

    result = data.merge(
        quality,
        on="experiment_id",
        how="left",
        validate="one_to_one",
    )

    if result[FIT_QUALITY_COLUMNS].isna().any().any():
        raise ValueError("Some parameter sets are missing fit-quality metrics.")

    return result


def select_shape_extremes(
    data: pd.DataFrame,
    n: int = 10,
) -> pd.DataFrame:
    if n <= 0:
        raise ValueError("n must be positive.")

    columns = [
        "experiment_id",
        "oil_id",
        "distribution_regime",
        "dispersion_tag",
        "nozzle_diameter",
        "has_gas",
        "shape",
        "scale",
        "rr_d50",
        "cdf_rmse",
        "cdf_max_error",
        "cdf_mass_rmse",
        "cdf_mass_max_error",
        "cdf_total_variation",
    ]

    lowest = data.nsmallest(
        n,
        "shape",
    )[columns].copy()

    lowest.insert(
        0,
        "extreme",
        "lowest",
    )

    highest = data.nlargest(
        n,
        "shape",
    )[columns].copy()

    highest.insert(
        0,
        "extreme",
        "highest",
    )

    return pd.concat(
        [
            lowest,
            highest,
        ],
        ignore_index=True,
    )
