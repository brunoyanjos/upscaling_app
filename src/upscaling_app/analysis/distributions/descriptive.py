import numpy as np
import pandas as pd


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

    mean, variance, std = discrete_moments(
        diameter,
        fraction,
    )

    d10 = empirical_quantile(
        diameter,
        fraction,
        0.10,
    )

    d50 = empirical_quantile(
        diameter,
        fraction,
        0.50,
    )

    d90 = empirical_quantile(
        diameter,
        fraction,
        0.90,
    )

    d_peak = diameter[np.argmax(fraction)]

    span = (d90 - d10) / d50

    cv = std / mean

    return pd.Series(
        {
            "d10": d10,
            "d50": d50,
            "d90": d90,
            "d_peak": d_peak,
            "mean_diameter": mean,
            "std_diameter": std,
            "cv": cv,
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
        "d_peak",
        "mean_diameter",
        "std_diameter",
        "span",
        "volume_fraction_sum",
    ]

    return result[columns]


def normalize_distribution(
    fraction: np.ndarray,
) -> np.ndarray:
    fraction = np.asarray(fraction, dtype=float)

    if not np.all(np.isfinite(fraction)):
        raise ValueError("Distribution contains non-finite fractions.")

    if np.any(fraction < 0.0):
        raise ValueError("Distribution contains negative fractions.")

    total = fraction.sum()

    if total <= 0.0:
        raise ValueError("Distribution has zero total volume fraction.")

    return fraction / total


def empirical_cdf(
    fraction: np.ndarray,
) -> np.ndarray:
    weights = normalize_distribution(fraction)

    return np.cumsum(weights)


def empirical_quantile(
    diameter: np.ndarray,
    fraction: np.ndarray,
    quantile: float,
) -> float:
    diameter = np.asarray(diameter, dtype=float)
    fraction = np.asarray(fraction, dtype=float)

    if diameter.size != fraction.size:
        raise ValueError("diameter and fraction must have the same size.")

    if not 0.0 <= quantile <= 1.0:
        raise ValueError("quantile must be between 0 and 1.")

    order = np.argsort(diameter)

    diameter = diameter[order]
    fraction = fraction[order]

    cumulative = empirical_cdf(fraction)

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


def discrete_moments(
    diameter: np.ndarray,
    fraction: np.ndarray,
) -> tuple[float, float, float]:
    diameter = np.asarray(diameter, dtype=float)
    fraction = np.asarray(fraction, dtype=float)

    if diameter.size != fraction.size:
        raise ValueError("diameter and fraction must have the same size.")

    weights = normalize_distribution(fraction)

    mean = np.sum(weights * diameter)

    variance = np.sum(weights * (diameter - mean) ** 2)

    std = np.sqrt(variance)

    return (
        float(mean),
        float(variance),
        float(std),
    )


def discrete_shape_statistics(
    diameter: np.ndarray,
    fraction: np.ndarray,
) -> tuple[float, float]:
    diameter = np.asarray(
        diameter,
        dtype=float,
    )

    fraction = np.asarray(
        fraction,
        dtype=float,
    )

    weights = normalize_distribution(fraction)

    mean = np.sum(weights * diameter)

    variance = np.sum(weights * (diameter - mean) ** 2)

    std = np.sqrt(variance)

    third_moment = np.sum(weights * (diameter - mean) ** 3)

    fourth_moment = np.sum(weights * (diameter - mean) ** 4)

    skewness = third_moment / std**3
    kurtosis = fourth_moment / std**4

    return (
        float(skewness),
        float(kurtosis),
    )


def geometric_bin_edges(
    diameter: np.ndarray,
) -> np.ndarray:
    diameter = np.asarray(
        diameter,
        dtype=float,
    )

    if np.any(diameter <= 0.0):
        raise ValueError("diameter must be positive.")

    edges = np.empty(
        diameter.size + 1,
        dtype=float,
    )

    edges[1:-1] = np.sqrt(diameter[:-1] * diameter[1:])
    edges[0] = diameter[0] ** 2 / edges[1]
    edges[-1] = diameter[-1] ** 2 / edges[-2]

    return edges


def experimental_pdf(
    diameter: np.ndarray,
    fraction: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    weights = normalize_distribution(fraction)

    edges = geometric_bin_edges(diameter)
    widths = np.diff(edges)
    density = weights / widths

    return edges, density


def geometric_bin_edges(
    diameter: np.ndarray,
) -> np.ndarray:
    diameter = np.asarray(
        diameter,
        dtype=float,
    )

    if diameter.ndim != 1:
        raise ValueError("diameter must be one-dimensional.")

    if diameter.size < 2:
        raise ValueError("At least two diameter bins are required.")

    if not np.all(np.isfinite(diameter)):
        raise ValueError("diameter contains non-finite values.")

    if np.any(diameter <= 0.0):
        raise ValueError("diameter must be positive.")

    if np.any(np.diff(diameter) <= 0.0):
        raise ValueError("diameter must be strictly increasing.")

    edges = np.empty(
        diameter.size + 1,
        dtype=float,
    )

    edges[1:-1] = np.sqrt(diameter[:-1] * diameter[1:])

    edges[0] = diameter[0] ** 2 / edges[1]

    edges[-1] = diameter[-1] ** 2 / edges[-2]

    return edges


def experimental_pdf(
    diameter: np.ndarray,
    fraction: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    diameter = np.asarray(
        diameter,
        dtype=float,
    )

    fraction = np.asarray(
        fraction,
        dtype=float,
    )

    if diameter.size != fraction.size:
        raise ValueError("diameter and fraction must have the same size.")

    order = np.argsort(diameter)

    diameter = diameter[order]
    fraction = fraction[order]

    weights = normalize_distribution(fraction)

    edges = geometric_bin_edges(diameter)

    widths = edges[1:] - edges[:-1]

    density = weights / widths

    return (
        diameter,
        edges,
        density,
    )


def volume_to_number_fraction(
    diameter: np.ndarray,
    volume_fraction: np.ndarray,
) -> np.ndarray:
    diameter = np.asarray(
        diameter,
        dtype=float,
    )

    volume_fraction = np.asarray(
        volume_fraction,
        dtype=float,
    )

    if diameter.size != volume_fraction.size:
        raise ValueError("diameter and volume_fraction must have the same size.")

    if np.any(diameter <= 0.0):
        raise ValueError("diameter must be positive.")

    volume_weights = normalize_distribution(volume_fraction)

    number_weights = volume_weights / diameter**3

    number_weights /= number_weights.sum()

    return number_weights
