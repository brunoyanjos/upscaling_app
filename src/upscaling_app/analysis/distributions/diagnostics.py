import numpy as np


def cumulative_at_diameter(
    diameter: np.ndarray,
    fraction: np.ndarray,
    target_diameter: float,
) -> float:
    diameter = np.asarray(diameter, dtype=float)
    fraction = np.asarray(fraction, dtype=float)

    if diameter.size != fraction.size:
        raise ValueError("diameter and fraction must have the same size.")

    total = fraction.sum()

    if total <= 0.0:
        raise ValueError("Distribution has zero total volume fraction.")

    order = np.argsort(diameter)

    diameter = diameter[order]
    fraction = fraction[order]

    weights = fraction / total
    cumulative = np.cumsum(weights)

    return float(
        np.interp(
            target_diameter,
            diameter,
            cumulative,
            left=0.0,
            right=1.0,
        )
    )
