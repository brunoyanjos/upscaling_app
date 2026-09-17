import pandas as pd

from upscaling_app import paths


def save_ssdi_results(results: pd.DataFrame) -> None:
    paths.RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if paths.SSDI_RESULTS.exists():
        existing = pd.read_excel(paths.SSDI_RESULTS)

        model_versions = results["model_version"].unique()

        existing = existing.loc[~existing["model_version"].isin(model_versions)]

        results = pd.concat(
            [existing, results],
            ignore_index=True,
        )

    results.to_excel(
        paths.SSDI_RESULTS,
        index=False,
    )
