import numpy as np

from scipy.optimize import brentq
from scipy.special import gamma


def rosin_rammler_moments(
    shape: float,
    scale: float,
) -> tuple[float, float]:
    mean = scale * gamma(1.0 + 1.0 / shape)

    variance = scale**2 * (gamma(1.0 + 2.0 / shape) - gamma(1.0 + 1.0 / shape) ** 2)

    std = np.sqrt(variance)

    return (
        float(mean),
        float(std),
    )


def estimate_rosin_rammler_from_moments(
    mean: float,
    std: float,
) -> tuple[float, float]:
    if mean <= 0.0:
        raise ValueError("mean must be positive.")

    if std <= 0.0:
        raise ValueError("std must be positive.")

    cv = std / mean

    def residual(shape: float) -> float:
        return gamma(1.0 + 2.0 / shape) / gamma(1.0 + 1.0 / shape) ** 2 - 1.0 - cv**2

    shape = brentq(
        residual,
        0.1,
        100.0,
    )

    scale = mean / gamma(1.0 + 1.0 / shape)

    return (
        float(shape),
        float(scale),
    )


def rosin_rammler_quantile(
    quantile: float,
    shape: float,
    scale: float,
) -> float:
    if not 0.0 < quantile < 1.0:
        raise ValueError("quantile must be between 0 and 1.")

    return float(scale * (-np.log(1.0 - quantile)) ** (1.0 / shape))


def rosin_rammler_cdf(
    diameter: np.ndarray,
    shape: float,
    scale: float,
) -> np.ndarray:
    diameter = np.asarray(
        diameter,
        dtype=float,
    )

    if np.any(diameter < 0.0):
        raise ValueError("diameter must be non-negative.")

    return 1.0 - np.exp(-((diameter / scale) ** shape))


def rosin_rammler_shape_statistics(
    shape: float,
    scale: float,
) -> tuple[float, float]:
    m1 = scale * gamma(1.0 + 1.0 / shape)

    m2 = scale**2 * gamma(1.0 + 2.0 / shape)

    m3 = scale**3 * gamma(1.0 + 3.0 / shape)

    m4 = scale**4 * gamma(1.0 + 4.0 / shape)

    variance = m2 - m1**2

    std = np.sqrt(variance)

    third_central_moment = m3 - 3.0 * m2 * m1 + 2.0 * m1**3

    fourth_central_moment = m4 - 4.0 * m3 * m1 + 6.0 * m2 * m1**2 - 3.0 * m1**4

    skewness = third_central_moment / std**3

    kurtosis = fourth_central_moment / std**4

    return (
        float(skewness),
        float(kurtosis),
    )


def rosin_rammler_pdf(
    diameter: np.ndarray,
    shape: float,
    scale: float,
) -> np.ndarray:
    diameter = np.asarray(
        diameter,
        dtype=float,
    )

    if np.any(diameter < 0.0):
        raise ValueError("diameter must be non-negative.")

    return (
        shape
        / scale
        * (diameter / scale) ** (shape - 1.0)
        * np.exp(-((diameter / scale) ** shape))
    )
