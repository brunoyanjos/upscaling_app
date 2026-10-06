import pandas as pd

from upscaling_app import paths

REQUIRED_PARAMETER_COLUMNS = [
    "experiment_id",
    "cdf_shape",
    "cdf_scale",
    "moment_shape",
    "moment_scale",
]


def save_distribution_parameters(
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

    if parameters["experiment_id"].duplicated().any():
        raise ValueError(
            "Distribution parameters contain duplicated " "experiment_id values."
        )

    output = (
        parameters[REQUIRED_PARAMETER_COLUMNS]
        .sort_values("experiment_id")
        .reset_index(drop=True)
    )

    path = paths.DISTRIBUTION_PARAMETERS_PATH

    path.parent.mkdir(parents=True, exist_ok=True)

    output.to_excel(path, index=False)
