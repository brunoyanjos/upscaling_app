import pandas as pd

from upscaling_app import paths


def load_ssdi_results(
    model_version: str,
) -> pd.DataFrame:
    results = pd.read_excel(paths.SSDI_RESULTS)

    results = results.loc[results["model_version"] == model_version].copy()

    return results.reset_index(drop=True)
