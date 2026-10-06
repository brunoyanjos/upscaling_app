import pandas as pd

from upscaling_app.upscaling.distributions.fitting import (
    fit_rosin_rammler,
    fit_rosin_rammler_from_moments,
)
from upscaling_app.upscaling.distributions.representation import (
    empirical_cdf,
    experimental_pdf,
)


def fit_distribution_parameters(
    distributions: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for (
        experiment_id,
        distribution,
    ) in distributions.groupby(
        "experiment_id",
        sort=False,
    ):
        distribution = distribution.sort_values("droplet_diameter").reset_index(
            drop=True
        )

        diameter = distribution["droplet_diameter"].to_numpy(dtype=float)

        volume_fraction = distribution["volume_fraction"].to_numpy(dtype=float)

        cumulative_fraction = empirical_cdf(volume_fraction)

        pdf_edges, _ = experimental_pdf(
            diameter=diameter,
            volume_fraction=volume_fraction,
        )

        cdf_diameter = pdf_edges[1:]

        # Method A — direct CDF fit
        cdf_shape, cdf_scale = fit_rosin_rammler(
            diameter=cdf_diameter,
            cumulative_fraction=cumulative_fraction,
        )

        # Method B — discrete moments
        moment_shape, moment_scale = fit_rosin_rammler_from_moments(
            diameter=diameter,
            volume_fraction=volume_fraction,
        )

        rows.append(
            {
                "experiment_id": experiment_id,
                "cdf_shape": cdf_shape,
                "cdf_scale": cdf_scale,
                "moment_shape": moment_shape,
                "moment_scale": moment_scale,
            }
        )

    return pd.DataFrame(rows)
