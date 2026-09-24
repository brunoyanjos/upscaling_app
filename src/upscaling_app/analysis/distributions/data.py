import pandas as pd

from upscaling_app import paths

DISTRIBUTION_COLUMNS = [
    "experiment_id",
    "droplet_diameter",
    "volume_fraction",
]

EXPERIMENT_COLUMNS = [
    "experiment_id",
    "oil_id",
    "dispersion_tag",
    "nozzle_diameter",
    "has_gas",
    "measured_d50",
    "source_sheet",
]


def load_distributions() -> pd.DataFrame:
    path = paths.DATABASE_DIR / "distributions.xlsx"

    data = pd.read_excel(
        path,
        usecols=DISTRIBUTION_COLUMNS,
    )

    return data.sort_values(["experiment_id", "droplet_diameter"]).reset_index(
        drop=True
    )


def load_experiments() -> pd.DataFrame:
    path = paths.DATABASE_DIR / "experiments.xlsx"

    data = pd.read_excel(
        path,
        usecols=EXPERIMENT_COLUMNS,
    )

    if data["experiment_id"].duplicated().any():
        raise ValueError("experiments.xlsx contains duplicated experiment_id values.")

    return data.reset_index(drop=True)
