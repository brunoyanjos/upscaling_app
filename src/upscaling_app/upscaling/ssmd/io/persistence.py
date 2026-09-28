from __future__ import annotations

from pathlib import Path

import pandas as pd

from upscaling_app import paths


def save_predictions(
    predictions: pd.DataFrame,
    path: Path = paths.SSMD_RESULTS,
) -> None:
    if "model_version" not in predictions.columns:
        raise ValueError("SSMD prediction table must contain 'model_version'.")

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_versions = predictions["model_version"].dropna().unique()

    if len(model_versions) == 0:
        raise ValueError("SSMD prediction table contains no model version.")

    if path.exists():
        existing = pd.read_excel(path)

        if "model_version" not in existing.columns:
            raise ValueError(
                "Existing SSMD results file does not contain "
                f"'model_version': {path}"
            )

        existing = existing.loc[
            ~existing["model_version"].isin(model_versions)
        ].copy()

        output = pd.concat(
            [
                existing,
                predictions,
            ],
            ignore_index=True,
        )

    else:
        output = predictions.copy()

    output.to_excel(
        path,
        index=False,
    )


def save_calibrations(
    calibrations: pd.DataFrame,
    path: Path = paths.SSMD_CALIBRATIONS,
) -> None:
    if "model_version" not in calibrations.columns:
        raise ValueError("SSMD calibration table must contain 'model_version'.")

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_versions = calibrations["model_version"].dropna().unique()

    if len(model_versions) == 0:
        raise ValueError("SSMD calibration table contains no model version.")

    if path.exists():
        existing = pd.read_excel(path)

        existing = existing.loc[
            ~existing["model_version"].isin(model_versions)
        ].copy()

        output = pd.concat(
            [existing, calibrations],
            ignore_index=True,
        )
    else:
        output = calibrations.copy()

    output = output.sort_values(
        ["model_version", "oil_id"],
    ).reset_index(drop=True)

    output.to_excel(
        path,
        index=False,
    )
