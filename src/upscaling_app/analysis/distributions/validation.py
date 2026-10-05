import pandas as pd

from upscaling_app.analysis.distributions.diagnostics import (
    cumulative_at_diameter,
)


import numpy as np


def compare_distribution_d50(
    summary: pd.DataFrame,
    experiments: pd.DataFrame,
) -> pd.DataFrame:
    comparison = summary[
        [
            "experiment_id",
            "d50",
            "d_peak",
        ]
    ].merge(
        experiments[
            [
                "experiment_id",
                "oil_id",
                "dispersion_tag",
                "nozzle_diameter",
                "has_gas",
                "measured_d50",
                "source_sheet",
            ]
        ],
        on="experiment_id",
        how="left",
        validate="one_to_one",
    )

    comparison["d50_error"] = comparison["d50"] - comparison["measured_d50"]

    comparison["d50_relative_error"] = (
        comparison["d50_error"] / comparison["measured_d50"]
    )

    comparison["d_peak_relative_error"] = (
        comparison["d_peak"] - comparison["measured_d50"]
    ) / comparison["measured_d50"]

    return comparison


def add_reported_d50_percentile(
    comparison: pd.DataFrame,
    distributions: pd.DataFrame,
) -> pd.DataFrame:
    target_d50 = comparison.set_index("experiment_id")["measured_d50"]

    diagnostics = []

    for experiment_id, distribution in distributions.groupby(
        "experiment_id",
        sort=False,
    ):
        if experiment_id not in target_d50.index:
            raise ValueError(f"Missing experiment metadata for {experiment_id}.")

        diameter = distribution["droplet_diameter"].to_numpy(dtype=float)

        fraction = distribution["volume_fraction"].to_numpy(dtype=float)

        measured_d50 = float(target_d50.loc[experiment_id])

        cdf_at_measured_d50 = cumulative_at_diameter(
            diameter=diameter,
            fraction=fraction,
            target_diameter=measured_d50,
        )

        diagnostics.append(
            {
                "experiment_id": experiment_id,
                "cdf_at_measured_d50": cdf_at_measured_d50,
                "reported_percentile": (100.0 * cdf_at_measured_d50),
                "percentile_error": (cdf_at_measured_d50 - 0.5),
            }
        )

    diagnostics = pd.DataFrame(diagnostics)

    return comparison.merge(
        diagnostics,
        on="experiment_id",
        how="left",
        validate="one_to_one",
    )


def cdf_error_metrics(
    reference: np.ndarray,
    prediction: np.ndarray,
) -> tuple[float, float, int]:
    reference = np.asarray(
        reference,
        dtype=float,
    )

    prediction = np.asarray(
        prediction,
        dtype=float,
    )

    if reference.shape != prediction.shape:
        raise ValueError("reference and prediction must have the same shape.")

    error = prediction - reference

    rmse = np.sqrt(np.mean(error**2))
    max_error_index = np.argmax(np.abs(error))
    max_absolute_error = np.abs(error[max_error_index])

    return (
        float(rmse),
        float(max_absolute_error),
        int(max_error_index),
    )
