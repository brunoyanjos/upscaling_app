import numpy as np

from upscaling_app.upscaling.distributions.representation import (
    normalize_volume_fraction,
)


def geometric_bin_edges(
    diameter: np.ndarray,
) -> np.ndarray:
    """Reconstruct geometric bin edges for PDF visualization only."""
    diameter = np.asarray(
        diameter,
        dtype=float,
    )

    if diameter.ndim != 1:
        raise ValueError("diameter must be one-dimensional.")

    if diameter.size < 2:
        raise ValueError("At least two diameter values are required.")

    if not np.all(np.isfinite(diameter)):
        raise ValueError("diameter contains non-finite values.")

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
) -> tuple[np.ndarray, np.ndarray]:
    """Construct a histogram density for plotting from discrete volume fractions.

    The reconstructed edges are not used for Rosin–Rammler calibration or CDF
    fit diagnostics; those remain aligned with the original diameter coordinates.
    """
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
