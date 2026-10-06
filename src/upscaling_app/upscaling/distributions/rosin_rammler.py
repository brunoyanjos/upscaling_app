import numpy as np


def rosin_rammler_cdf(
    diameter: np.ndarray,
    shape: float,
    scale: float,
) -> np.ndarray:
    diameter = np.asarray(diameter, dtype=float)

    if shape <= 0.0:
        raise ValueError("shape must be positive.")

    if scale <= 0.0:
        raise ValueError("scale must be positive.")

    if np.any(diameter < 0.0):
        raise ValueError("diameter must be non-negative.")

    return 1.0 - np.exp(-((diameter / scale) ** shape))


def rosin_rammler_pdf(
    diameter: np.ndarray,
    shape: float,
    scale: float,
) -> np.ndarray:
    diameter = np.asarray(diameter, dtype=float)

    if shape <= 0.0:
        raise ValueError("shape must be positive.")

    if scale <= 0.0:
        raise ValueError("scale must be positive.")

    if np.any(diameter < 0.0):
        raise ValueError("diameter must be non-negative.")

    scaled = diameter / scale

    return shape / scale * scaled ** (shape - 1.0) * np.exp(-(scaled**shape))


def rosin_rammler_quantile(
    quantile: float | np.ndarray,
    shape: float | np.ndarray,
    scale: float | np.ndarray,
) -> float | np.ndarray:
    quantile = np.asarray(
        quantile,
        dtype=float,
    )

    shape = np.asarray(
        shape,
        dtype=float,
    )

    scale = np.asarray(
        scale,
        dtype=float,
    )

    if np.any((quantile <= 0.0) | (quantile >= 1.0)):
        raise ValueError("quantile must be between 0 and 1.")

    if np.any(shape <= 0.0):
        raise ValueError("shape must be positive.")

    if np.any(scale <= 0.0):
        raise ValueError("scale must be positive.")

    result = scale * (-np.log(1.0 - quantile)) ** (1.0 / shape)

    if result.ndim == 0:
        return float(result)

    return result


def scale_from_d50(
    d50: float,
    shape: float,
) -> float:
    if d50 <= 0.0:
        raise ValueError("d50 must be positive.")

    if shape <= 0.0:
        raise ValueError("shape must be positive.")

    return float(d50 / np.log(2.0) ** (1.0 / shape))
