from __future__ import annotations

import numpy as np
import pandas as pd

EXPONENT = -3.0 / 5.0


def add_sintef_eta(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    result = dataset.copy()

    is_no_gas = ~result["has_gas"]
    is_gas = result["has_gas"]

    result["eta"] = np.select(
        [
            is_no_gas,
            is_gas,
        ],
        [
            0.85,
            0.6779545878291601,
        ],
        default=np.nan,
    )

    return result


def add_sintef_prediction(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    result = add_sintef_eta(dataset)

    is_3mm = result["nozzle_diameter"].eq(0.003) & ~result["has_gas"]
    is_2mm = result["nozzle_diameter"].eq(0.002) & ~result["has_gas"]
    is_2mm_gas = result["nozzle_diameter"].eq(0.002) & result["has_gas"]

    result["c_coef"] = np.select(
        [
            is_3mm,
            is_2mm,
            is_2mm_gas,
        ],
        [
            0.33063475973887657,
            0.46170083447858073,
            0.5720125321034614,
        ],
        default=np.nan,
    )

    result["d_coef"] = 0.05

    result["dR_pred"] = (
        result["eta"] * result["momentum_amplification"]
    ) ** EXPONENT * (
        result["c_coef"]
        + result["d_coef"] * result["oil_viscosity"] / result["untreated_ift"]
    )

    result["d50_pred"] = result["dR_pred"] * result["untreated_d50_pred"]

    return result
