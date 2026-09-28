import pandas as pd

from upscaling_app import paths


def load_ssdi_results(
    model_version: str,
) -> pd.DataFrame:
    results = pd.read_excel(paths.SSDI_RESULTS)

    results = results.loc[results["model_version"] == model_version].copy()

    return results.reset_index(drop=True)


def load_ssdi_calibrations(
    model_version: str,
) -> pd.DataFrame:
    calibrations = pd.read_excel(paths.SSDI_CALIBRATIONS)

    calibrations = calibrations.loc[
        calibrations["model_version"] == model_version
    ].copy()

    if calibrations.empty:
        raise ValueError(
            "No SSDI calibrations found for " f"model version {model_version!r}."
        )

    return calibrations
