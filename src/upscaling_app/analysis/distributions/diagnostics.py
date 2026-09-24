import numpy as np


def cumulative_at_diameter(
    diameter: np.ndarray,
    fraction: np.ndarray,
    target_diameter: float,
) -> float:
    fraction = fraction / fraction.sum()
    cumulative = np.cumsum(fraction)

    return float(
        np.interp(
            target_diameter,
            diameter,
            cumulative,
        )
    )
