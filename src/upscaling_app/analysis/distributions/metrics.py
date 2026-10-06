import numpy as np


def cdf_error_metrics(
    experimental: np.ndarray,
    predicted: np.ndarray,
) -> tuple[float, float]:
    experimental = np.asarray(
        experimental,
        dtype=float,
    )

    predicted = np.asarray(
        predicted,
        dtype=float,
    )

    if experimental.size != predicted.size:
        raise ValueError("experimental and predicted must have the same size.")

    error = predicted - experimental

    rmse = np.sqrt(np.mean(error**2))

    max_abs_error = np.max(np.abs(error))

    return (
        float(rmse),
        float(max_abs_error),
    )


def distribution_mass_metrics(
    experimental: np.ndarray,
    predicted: np.ndarray,
) -> tuple[float, float, float]:
    experimental = np.asarray(
        experimental,
        dtype=float,
    )

    predicted = np.asarray(
        predicted,
        dtype=float,
    )

    if experimental.size != predicted.size:
        raise ValueError("experimental and predicted must have the same size.")

    experimental = experimental / experimental.sum()

    predicted = predicted / predicted.sum()

    error = predicted - experimental

    rmse = np.sqrt(np.mean(error**2))

    max_abs_error = np.max(np.abs(error))

    total_variation = 0.5 * np.sum(np.abs(error))

    return (
        float(rmse),
        float(max_abs_error),
        float(total_variation),
    )
