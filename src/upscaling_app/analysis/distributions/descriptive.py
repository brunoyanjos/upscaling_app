import numpy as np
import pandas as pd


import numpy as np


def distribution_quantile(
    diameter: np.ndarray,
    fraction: np.ndarray,
    quantile: float,
) -> float:
    total = fraction.sum()

    if total <= 0.0:
        raise ValueError("Distribution has zero total volume fraction.")

    fraction = fraction / total
    cumulative = np.cumsum(fraction)

    upper_index = np.searchsorted(
        cumulative,
        quantile,
        side="left",
    )

    if upper_index == 0:
        return float(diameter[0])

    lower_index = upper_index - 1

    d0 = diameter[lower_index]
    d1 = diameter[upper_index]

    f0 = cumulative[lower_index]
    f1 = cumulative[upper_index]

    if np.isclose(f1, f0):
        return float(d1)

    alpha = (quantile - f0) / (f1 - f0)

    return float(d0 + alpha * (d1 - d0))


def summarize_distribution(
    distribution: pd.DataFrame,
) -> pd.Series:
    distribution = distribution.sort_values("droplet_diameter")

    diameter = distribution["droplet_diameter"].to_numpy(dtype=float)
    fraction = distribution["volume_fraction"].to_numpy(dtype=float)

    total_fraction = fraction.sum()

    if total_fraction <= 0.0:
        raise ValueError("Distribution has zero total volume fraction.")

    weights = fraction / total_fraction

    mean = np.sum(weights * diameter)

    variance = np.sum(weights * (diameter - mean) ** 2)

    std = np.sqrt(variance)

    d10 = distribution_quantile(
        diameter,
        fraction,
        0.10,
    )

    d50 = distribution_quantile(
        diameter,
        fraction,
        0.50,
    )

    d90 = distribution_quantile(
        diameter,
        fraction,
        0.90,
    )

    mode = diameter[np.argmax(fraction)]

    span = (d90 - d10) / d50

    return pd.Series(
        {
            "d10": d10,
            "d50": d50,
            "d90": d90,
            "mean_diameter": mean,
            "std_diameter": std,
            "mode_diameter": mode,
            "span": span,
            "volume_fraction_sum": total_fraction,
        }
    )


def summarize_distributions(
    data: pd.DataFrame,
) -> pd.DataFrame:
    summaries = []

    for experiment_id, distribution in data.groupby(
        "experiment_id",
        sort=False,
    ):
        summary = summarize_distribution(distribution)

        summary["experiment_id"] = experiment_id

        summaries.append(summary)

    result = pd.DataFrame(summaries)

    columns = [
        "experiment_id",
        "d10",
        "d50",
        "d90",
        "mean_diameter",
        "std_diameter",
        "mode_diameter",
        "span",
        "volume_fraction_sum",
    ]

    return result[columns]
