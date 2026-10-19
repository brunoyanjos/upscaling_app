from pathlib import Path

import numpy as np
import pandas as pd

GLOBAL_MODEL_NAMES = {
    "sintef_baseline": "SINTEF Reference",
    "jax_baseline_all": "Global — 10 oils",
    "jax_exclude_3016_4662_4665": "Retained — 7 oils",
}

MODEL_NAMES = {
    **GLOBAL_MODEL_NAMES,
    "jax_oil_wise": "Oil-wise",
}


def load_global_calibrations(
    predictions_path: Path,
) -> dict[str, tuple[float, float]]:
    """Load persisted SSDI coefficients without recalibration."""

    data = pd.read_excel(
        predictions_path,
        usecols=["model_version", "a_coef", "b_coef"],
    )

    calibrations = {}

    for version in GLOBAL_MODEL_NAMES:
        subset = data.loc[
            data["model_version"] == version,
            ["a_coef", "b_coef"],
        ]

        if subset.empty:
            raise ValueError(f"Missing calibration: {version}")

        coefficients = subset.to_numpy(dtype=float)

        if not np.isfinite(coefficients).all():
            raise ValueError(f"Invalid coefficients: {version}")

        if not np.allclose(
            coefficients,
            coefficients[0],
            rtol=1e-10,
            atol=1e-12,
        ):
            raise ValueError(f"Inconsistent stored coefficients: {version}")

        calibrations[version] = tuple(float(value) for value in coefficients[0])

    return calibrations


def load_oil_wise_calibrations(
    predictions_path: Path,
    experiments_path: Path,
) -> dict[int, tuple[float, float]]:
    """Load persisted oil-wise SSDI coefficients by oil_id."""

    predictions = pd.read_excel(
        predictions_path,
        usecols=[
            "experiment_id",
            "model_version",
            "a_coef",
            "b_coef",
        ],
    )

    predictions = predictions.loc[
        predictions["model_version"] == "jax_oil_wise",
        ["experiment_id", "a_coef", "b_coef"],
    ].copy()

    if predictions.empty:
        raise ValueError("No oil-wise calibrations found.")

    if predictions["experiment_id"].duplicated().any():
        raise ValueError("Duplicate oil-wise experiment IDs.")

    experiments = pd.read_excel(
        experiments_path,
        usecols=["experiment_id", "oil_id"],
    )

    if experiments["experiment_id"].duplicated().any():
        raise ValueError("Duplicate normalized experiment IDs.")

    joined = predictions.merge(
        experiments,
        on="experiment_id",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    if (joined["_merge"] != "both").any():
        raise ValueError("Oil-wise predictions contain unknown experiment IDs.")

    calibrations = {}

    for oil_id, group in joined.groupby("oil_id"):
        coefficients = group[["a_coef", "b_coef"]].to_numpy(dtype=float)

        if not np.isfinite(coefficients).all():
            raise ValueError(f"Invalid oil-wise coefficients: {oil_id}")

        if not np.allclose(
            coefficients,
            coefficients[0],
            rtol=1e-10,
            atol=1e-12,
        ):
            raise ValueError(f"Inconsistent oil-wise coefficients: {oil_id}")

        calibrations[int(oil_id)] = tuple(float(value) for value in coefficients[0])

    return calibrations
