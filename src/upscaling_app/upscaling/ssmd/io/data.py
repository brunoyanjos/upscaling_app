from __future__ import annotations

import pandas as pd

from upscaling_app import paths
from upscaling_app.upscaling.ssdi.versions import REFERENCE_VERSION

PAIR_KEYS = [
    "oil_id",
    "nozzle_diameter",
    "has_gas",
]


def load_experiments() -> pd.DataFrame:
    return pd.read_excel(paths.EXPERIMENTS_DATABASE)


def load_ssmd_experiments() -> pd.DataFrame:
    experiments = load_experiments()

    ssmd = experiments.loc[experiments["dispersion_kind"].eq("SSMD")].copy()

    return ssmd.reset_index(drop=True)


def load_ssdi_reference_predictions() -> pd.DataFrame:
    results = pd.read_excel(paths.RESULTS_DIR / "ssdi_results.xlsx")

    predictions = results.loc[
        results["model_version"].eq(REFERENCE_VERSION),
        [
            "experiment_id",
            "d50_pred",
        ],
    ].copy()

    return predictions.rename(
        columns={
            "experiment_id": "untreated_experiment_id",
            "d50_pred": "untreated_d50_pred",
        }
    )


def load_ssmd_calibration_dataset() -> pd.DataFrame:
    experiments = load_experiments()

    treated = experiments.loc[experiments["dispersion_kind"].eq("SSMD")].copy()
    untreated = experiments.loc[experiments["dispersion_kind"].eq("Untreated")].copy()

    duplicated_reference = untreated.duplicated(
        subset=PAIR_KEYS,
        keep=False,
    )

    if duplicated_reference.any():
        duplicated = untreated.loc[
            duplicated_reference,
            PAIR_KEYS + ["experiment_id", "dispersion_tag"],
        ]

        raise ValueError(
            "Multiple untreated references found for the same "
            "SSMD condition:\n"
            f"{duplicated.to_string(index=False)}"
        )

    untreated = untreated[
        PAIR_KEYS
        + [
            "experiment_id",
            "measured_d50",
            "oil_flow",
            "gas_flow",
            "oil_density",
            "gas_density",
            "ift",
        ]
    ].rename(
        columns={
            "experiment_id": "untreated_experiment_id",
            "measured_d50": "untreated_d50_measured",
            "oil_flow": "untreated_oil_flow",
            "gas_flow": "untreated_gas_flow",
            "oil_density": "untreated_oil_density",
            "gas_density": "untreated_gas_density",
            "ift": "untreated_ift",
        }
    )

    dataset = treated.merge(
        untreated,
        on=PAIR_KEYS,
        how="left",
        validate="many_to_one",
    )

    missing_reference = dataset["untreated_d50_measured"].isna()

    if missing_reference.any():
        missing = dataset.loc[
            missing_reference,
            [
                "experiment_id",
                "oil_id",
                "nozzle_diameter",
                "has_gas",
            ],
        ]

        raise ValueError(
            "Untreated reference not found for some SSMD experiments:\n"
            f"{missing.to_string(index=False)}"
        )

    ssdi_predictions = load_ssdi_reference_predictions()

    ssdi_predictions = ssdi_predictions.loc[
        ssdi_predictions["untreated_experiment_id"].isin(
            untreated["untreated_experiment_id"]
        )
    ].copy()

    dataset = dataset.merge(
        ssdi_predictions,
        on="untreated_experiment_id",
        how="left",
        validate="many_to_one",
    )

    missing_prediction = dataset["untreated_d50_pred"].isna()

    if missing_prediction.any():
        missing = dataset.loc[
            missing_prediction,
            [
                "oil_id",
                "nozzle_diameter",
                "has_gas",
                "untreated_experiment_id",
            ],
        ]

        raise ValueError(
            "SSDI prediction missing for some untreated references:\n"
            f"{missing.to_string(index=False)}"
        )

    return dataset.reset_index(drop=True)
