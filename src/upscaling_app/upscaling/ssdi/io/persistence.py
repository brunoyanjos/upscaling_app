import pandas as pd

from upscaling_app import paths


def _replace_model_versions(
    existing: pd.DataFrame,
    new_data: pd.DataFrame,
) -> pd.DataFrame:
    if "model_version" not in new_data.columns:
        raise ValueError("SSDI persisted data must contain a 'model_version' column.")

    if existing.empty:
        return new_data.copy()

    if "model_version" not in existing.columns:
        raise ValueError(
            "Existing SSDI persisted data does not contain a " "'model_version' column."
        )

    model_versions = new_data["model_version"].dropna().unique()

    existing = existing.loc[~existing["model_version"].isin(model_versions)]

    return pd.concat(
        [existing, new_data],
        ignore_index=True,
    )


def _load_table(
    path,
) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    return pd.read_excel(path)


def save_ssdi_results(
    results: pd.DataFrame,
) -> None:
    output = paths.SSDI_PREDICTIONS_PATH

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    existing = _load_table(output)

    results = _replace_model_versions(
        existing=existing,
        new_data=results,
    )

    results.to_excel(
        output,
        index=False,
    )


def save_ssdi_calibrations(
    calibrations: pd.DataFrame,
) -> None:
    output = paths.SSDI_CALIBRATIONS_PATH

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    existing = _load_table(output)

    calibrations = _replace_model_versions(
        existing=existing,
        new_data=calibrations,
    )

    sort_columns = [
        column
        for column in (
            "model_version",
            "oil_id",
        )
        if column in calibrations.columns
    ]

    if sort_columns:
        calibrations = calibrations.sort_values(sort_columns).reset_index(drop=True)

    calibrations.to_excel(
        output,
        index=False,
    )
