from __future__ import annotations

from time import perf_counter

import pandas as pd

from upscaling_app.analysis.experimental.data import load_distributions
from upscaling_app.upscaling.distributions.fitting import fit_rosin_rammler
from upscaling_app.upscaling.distributions.persistence import (
    save_distribution_parameters,
)
from upscaling_app.upscaling.distributions.reporting import (
    report_distribution_fit,
)
from upscaling_app.upscaling.distributions.representation import empirical_cdf


def fit_distribution_parameters(
    distributions: pd.DataFrame,
) -> pd.DataFrame:
    required_columns = {
        "experiment_id",
        "droplet_diameter",
        "volume_fraction",
    }

    missing = required_columns.difference(distributions.columns)

    if missing:
        raise ValueError(
            "Distribution data is missing required columns: "
            + ", ".join(sorted(missing))
        )

    if distributions.empty:
        raise ValueError("No experimental distributions available for fitting.")

    if distributions["experiment_id"].isna().any():
        raise ValueError("Distribution data contains missing experiment_id values.")

    rows: list[dict[str, float | str]] = []

    for experiment_id, distribution in distributions.groupby(
        "experiment_id",
        sort=False,
    ):
        distribution = distribution.sort_values("droplet_diameter").reset_index(
            drop=True
        )

        diameter = distribution["droplet_diameter"].to_numpy(dtype=float)

        volume_fraction = distribution["volume_fraction"].to_numpy(dtype=float)

        cumulative_fraction = empirical_cdf(volume_fraction)

        shape, scale = fit_rosin_rammler(
            diameter=diameter,
            cumulative_fraction=cumulative_fraction,
        )

        rows.append(
            {
                "experiment_id": experiment_id,
                "shape": shape,
                "scale": scale,
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "experiment_id",
            "shape",
            "scale",
        ],
    )


def run_distribution_fit_workflow() -> pd.DataFrame:
    start_time = perf_counter()

    distributions = load_distributions()

    parameters = fit_distribution_parameters(distributions)

    save_distribution_parameters(parameters)

    elapsed_seconds = perf_counter() - start_time

    report_distribution_fit(
        parameters=parameters,
        elapsed_seconds=elapsed_seconds,
    )

    return parameters
