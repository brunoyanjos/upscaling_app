import numpy as np
from scipy.optimize import least_squares

from upscaling_app.upscaling.distributions.rosin_rammler import (
    rosin_rammler_cdf,
)


def fit_rosin_rammler(
    diameter: np.ndarray,
    cumulative_fraction: np.ndarray,
) -> tuple[float, float]:
    diameter = np.asarray(diameter, dtype=float)
    cumulative_fraction = np.asarray(cumulative_fraction, dtype=float)

    if diameter.ndim != 1 or cumulative_fraction.ndim != 1:
        raise ValueError("diameter and cumulative_fraction must be one-dimensional.")

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

    if np.any(np.diff(diameter) <= 0.0):
        raise ValueError("diameter must contain unique values.")

    if np.any(np.diff(cumulative_fraction) < 0.0):
        raise ValueError("cumulative_fraction must be non-decreasing.")

    target_probability = 1.0 - np.exp(-1.0)
    # Search the first crossing; the empirical CDF may contain plateaus.
    crossing = int(
        np.searchsorted(cumulative_fraction, target_probability, side="left")
    )
    if crossing == 0:
        initial_scale = float(diameter[0])
    elif crossing == diameter.size:
        initial_scale = float(diameter[-1])
    else:
        probability_left = cumulative_fraction[crossing - 1]
        probability_right = cumulative_fraction[crossing]
        fraction = (target_probability - probability_left) / (
            probability_right - probability_left
        )
        initial_scale = float(
            diameter[crossing - 1]
            + fraction * (diameter[crossing] - diameter[crossing - 1])
        )
    initial_shape = 2.0

    def residual(parameters: np.ndarray) -> np.ndarray:
        shape, scale = parameters

        predicted = rosin_rammler_cdf(
            diameter=diameter,
            shape=shape,
            scale=scale,
        )

        return predicted - cumulative_fraction

    result = least_squares(
        residual,
        x0=np.array([initial_shape, initial_scale], dtype=float),
        bounds=(
            np.finfo(float).eps,
            np.inf,
        ),
        x_scale="jac",
    )

    if not result.success:
        raise RuntimeError(f"Rosin-Rammler fitting failed: {result.message}")

    shape, scale = result.x

    return float(shape), float(scale)
