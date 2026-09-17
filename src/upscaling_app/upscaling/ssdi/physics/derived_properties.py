import math

import pandas as pd

GRAVITY = 9.81
RHO_SEAWATER = 1024.0


def add_ssdi_physics(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    total_flow = result["oil_flow"] + result["gas_flow"].fillna(0.0)

    result["void_fraction"] = result["gas_flow"].fillna(0.0) / total_flow

    result["mixed_density"] = (
        result["gas_density"].fillna(0.0) * result["gas_flow"].fillna(0.0)
        + result["oil_density"] * result["oil_flow"]
    ) / total_flow

    result["volumetric_velocity"] = total_flow / (
        0.25 * math.pi * result["nozzle_diameter"] ** 2
    )

    result["modified_velocity"] = (
        result["volumetric_velocity"]
        * (result["mixed_density"] / result["oil_density"]) ** 0.5
    )

    result["reduced_gravity"] = GRAVITY * (1.0 - result["mixed_density"] / RHO_SEAWATER)
    result["froude"] = (
        result["modified_velocity"]
        / (result["reduced_gravity"] * result["nozzle_diameter"]) ** 0.5
    )

    result["effective_velocity"] = result["modified_velocity"] * (
        1.0 + 1.0 / result["froude"]
    )

    result["reynolds"] = (
        result["oil_density"]
        * result["effective_velocity"]
        * result["nozzle_diameter"]
        / result["oil_viscosity"]
    )

    result["weber"] = (
        result["oil_density"]
        * result["effective_velocity"] ** 2
        * result["nozzle_diameter"]
        / result["ift"]
    )

    result["capillary"] = result["weber"] / result["reynolds"]

    return result
