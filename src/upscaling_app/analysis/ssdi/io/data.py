import pandas as pd

from upscaling_app import paths


def load_ssdi_results(
    model_version: str,
) -> pd.DataFrame:
    if not paths.SSDI_PREDICTIONS_PATH.exists():
        raise FileNotFoundError(
            "SSDI predictions not found. " f"Expected {paths.SSDI_PREDICTIONS_PATH}."
        )

    results = pd.read_excel(
        paths.SSDI_PREDICTIONS_PATH,
    )

    results = results.loc[results["model_version"] == model_version].copy()

    if results.empty:
        raise ValueError(
            "No SSDI predictions found for " f"model version {model_version!r}."
        )

    return results.reset_index(drop=True)


def load_ssdi_calibrations(
    model_version: str,
) -> pd.DataFrame:
    if not paths.SSDI_CALIBRATIONS_PATH.exists():
        raise FileNotFoundError(
            "SSDI calibrations not found. " f"Expected {paths.SSDI_CALIBRATIONS_PATH}."
        )

    calibrations = pd.read_excel(
        paths.SSDI_CALIBRATIONS_PATH,
    )

    calibrations = calibrations.loc[
        calibrations["model_version"] == model_version
    ].copy()

    if calibrations.empty:
        raise ValueError(
            "No SSDI calibrations found for " f"model version {model_version!r}."
        )

    return calibrations.reset_index(drop=True)
