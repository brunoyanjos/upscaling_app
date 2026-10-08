import numpy as np
import pandas as pd

from upscaling_app import paths

REQUIRED_PARAMETER_COLUMNS = [
    "experiment_id",
    "shape",
    "scale",
]


def _validate_distribution_parameters(
    parameters: pd.DataFrame,
) -> None:
    missing = [
        column
        for column in REQUIRED_PARAMETER_COLUMNS
        if column not in parameters.columns
    ]

    if missing:
        raise ValueError(
            "Missing distribution parameter columns: " + ", ".join(missing)
        )

    if parameters.empty:
        raise ValueError("No distribution parameters available for persistence.")

    if parameters["experiment_id"].isna().any():
        raise ValueError("Distribution parameters contain missing experiment_id values.")

    if parameters["experiment_id"].duplicated().any():
        raise ValueError(
            "Distribution parameters contain duplicated experiment_id values."
        )

    for column in ("shape", "scale"):
        values = parameters[column].to_numpy(dtype=float)
        invalid = ~np.isfinite(values) | (values <= 0.0)

        if invalid.any():
            invalid_rows = parameters.loc[
                invalid,
                ["experiment_id", column],
            ]
            raise ValueError(
                f"Invalid Rosin-Rammler {column} values:\n"
                f"{invalid_rows.to_string(index=False)}"
            )


def save_distribution_parameters(
    parameters: pd.DataFrame,
) -> None:
    _validate_distribution_parameters(parameters)

    output = (
        parameters[REQUIRED_PARAMETER_COLUMNS]
        .sort_values("experiment_id")
        .reset_index(drop=True)
    )

    path = paths.DISTRIBUTION_PARAMETERS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    output.to_excel(path, index=False)


def load_distribution_parameters() -> pd.DataFrame:
    if not paths.DISTRIBUTION_PARAMETERS_PATH.exists():
        raise FileNotFoundError(
            "Distribution parameters not found. "
            "Run 'upscaling distributions fit' first."
        )

    parameters = pd.read_excel(paths.DISTRIBUTION_PARAMETERS_PATH)
    _validate_distribution_parameters(parameters)

    return parameters[REQUIRED_PARAMETER_COLUMNS].copy()
