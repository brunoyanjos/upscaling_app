import numpy as np


def normalize_volume_fraction(
    volume_fraction: np.ndarray,
) -> np.ndarray:
    volume_fraction = np.asarray(volume_fraction, dtype=float)

    if volume_fraction.ndim != 1:
        raise ValueError("volume_fraction must be one-dimensional.")

    if not np.all(np.isfinite(volume_fraction)):
        raise ValueError("volume_fraction contains non-finite values.")

    if np.any(volume_fraction < 0.0):
        raise ValueError("volume_fraction contains negative values.")

    total = volume_fraction.sum()

    if total <= 0.0:
        raise ValueError("volume_fraction has zero total volume.")

    return volume_fraction / total


def empirical_cdf(
    volume_fraction: np.ndarray,
) -> np.ndarray:
    """CDF values aligned to the original experimental diameter coordinates."""
    weights = normalize_volume_fraction(volume_fraction)

    cumulative = np.cumsum(weights)
    cumulative = np.clip(cumulative, 0.0, 1.0)
    cumulative[-1] = 1.0

    return cumulative
