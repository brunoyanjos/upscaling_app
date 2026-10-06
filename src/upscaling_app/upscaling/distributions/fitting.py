import numpy as np
from scipy.optimize import least_squares

from scipy.optimize import brentq
from scipy.special import gamma

from upscaling_app.upscaling.distributions.rosin_rammler import (
    rosin_rammler_cdf,
)


def fit_rosin_rammler(
    diameter: np.ndarray,
    cumulative_fraction: np.ndarray,
) -> tuple[float, float]:
    diameter = np.asarray(diameter, dtype=float)
    cumulative_fraction = np.asarray(cumulative_fraction, dtype=float)

    if diameter.size != cumulative_fraction.size:
        raise ValueError("diameter and cumulative_fraction must have the same size.")

    if diameter.size < 2:
        raise ValueError("At least two distribution points are required.")

    if not np.all(np.isfinite(diameter)):
        raise ValueError("diameter contains non-finite values.")

    if not np.all(np.isfinite(cumulative_fraction)):
        raise ValueError("cumulative_fraction contains non-finite values.")

    if np.any(diameter <= 0.0):
        raise ValueError("diameter must be positive.")

    if np.any((cumulative_fraction < 0.0) | (cumulative_fraction > 1.0)):
        raise ValueError("cumulative_fraction must be between 0 and 1.")

    order = np.argsort(diameter)

    diameter = diameter[order]
    cumulative_fraction = cumulative_fraction[order]

    if np.any(np.diff(cumulative_fraction) < 0.0):
        raise ValueError("cumulative_fraction must be non-decreasing.")

    target_probability = 1.0 - np.exp(-1.0)

    initial_scale = float(
        np.interp(
            target_probability,
            cumulative_fraction,
            diameter,
        )
    )

    initial_shape = 2.0

    def residual(
        parameters: np.ndarray,
    ) -> np.ndarray:
        shape = parameters[0]
        scale = parameters[1]

        predicted = rosin_rammler_cdf(
            diameter=diameter,
            shape=shape,
            scale=scale,
        )

        return predicted - cumulative_fraction

    result = least_squares(
        residual,
        x0=np.array(
            [
                initial_shape,
                initial_scale,
            ]
        ),
        bounds=(
            np.finfo(float).eps,
            np.inf,
        ),
        x_scale="jac",
    )

    if not result.success:
        raise RuntimeError("Rosin-Rammler fitting failed: " f"{result.message}")

    shape = float(result.x[0])
    scale = float(result.x[1])

    return shape, scale


def fit_rosin_rammler_from_moments(
    diameter: np.ndarray,
    volume_fraction: np.ndarray,
) -> tuple[float, float]:
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

    weights = volume_fraction / volume_fraction.sum()

    mean = np.sum(weights * diameter)

    variance = np.sum(weights * (diameter - mean) ** 2)

    std = np.sqrt(variance)

    cv_squared = (std / mean) ** 2

    def residual(
        shape: float,
    ) -> float:
        return (
            gamma(1.0 + 2.0 / shape) / gamma(1.0 + 1.0 / shape) ** 2 - 1.0 - cv_squared
        )

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
