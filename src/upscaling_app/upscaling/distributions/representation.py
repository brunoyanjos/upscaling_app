import numpy as np


def normalize_volume_fraction(
    volume_fraction: np.ndarray,
) -> np.ndarray:
    volume_fraction = np.asarray(
        volume_fraction,
        dtype=float,
    )

    if not np.all(np.isfinite(volume_fraction)):
        raise ValueError("volume_fraction contains non-finite values.")

    if np.any(volume_fraction < 0.0):
        raise ValueError("volume_fraction contains negative values.")

    total = volume_fraction.sum()

    if total <= 0.0:
        raise ValueError("volume_fraction has zero total mass.")

    return volume_fraction / total


def empirical_cdf(
    volume_fraction: np.ndarray,
) -> np.ndarray:
    weights = normalize_volume_fraction(volume_fraction)

    cumulative = np.cumsum(weights)
    cumulative = np.clip(cumulative, 0.0, 1.0)
    cumulative[-1] = 1.0

    return cumulative


def geometric_bin_edges(
    diameter: np.ndarray,
) -> np.ndarray:
    diameter = np.asarray(
        diameter,
        dtype=float,
    )

    if diameter.size < 2:
        raise ValueError("At least two diameter values are required.")

    if np.any(diameter <= 0.0):
        raise ValueError("diameter must be positive.")

    if np.any(np.diff(diameter) <= 0.0):
        raise ValueError("diameter must be strictly increasing.")

    internal_edges = np.sqrt(diameter[:-1] * diameter[1:])

    first_edge = diameter[0] ** 2 / internal_edges[0]
    last_edge = diameter[-1] ** 2 / internal_edges[-1]

    return np.concatenate(
        (
            [first_edge],
            internal_edges,
            [last_edge],
        )
    )


def experimental_pdf(
    diameter: np.ndarray,
    volume_fraction: np.ndarray,
) -> tuple[
    np.ndarray,
    np.ndarray,
]:
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

    weights = normalize_volume_fraction(volume_fraction)

    edges = geometric_bin_edges(diameter)

    widths = np.diff(edges)

    density = weights / widths

    return edges, density
