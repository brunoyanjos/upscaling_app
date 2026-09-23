from __future__ import annotations

import numpy as np
import pandas as pd

WATER_DENSITY = 1000.0  # kg/m³
SEAWATER_DENSITY = 1024.0  # kg/m³
GRAVITY = 9.81  # m/s²


def add_untreated_hydrodynamics(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    result = dataset.copy()

    nozzle_area = np.pi * result["nozzle_diameter"] ** 2 / 4.0

    total_flow = result["untreated_oil_flow"] + result["untreated_gas_flow"]

    result["untreated_gas_void_fraction"] = result["untreated_gas_flow"] / total_flow

    result["untreated_mixed_density"] = (
        result["untreated_oil_density"] * result["untreated_oil_flow"]
        + result["untreated_gas_density"] * result["untreated_gas_flow"]
    ) / total_flow

    result["untreated_volumetric_velocity"] = total_flow / nozzle_area

    result["untreated_modified_velocity"] = result[
        "untreated_volumetric_velocity"
    ] * np.sqrt(result["untreated_mixed_density"] / result["untreated_oil_density"])

    result["untreated_reduced_gravity"] = (
        GRAVITY
        * (SEAWATER_DENSITY - result["untreated_mixed_density"])
        / SEAWATER_DENSITY
    )

    result["untreated_froude"] = result["untreated_modified_velocity"] / np.sqrt(
        result["untreated_reduced_gravity"] * result["nozzle_diameter"]
    )

    result["untreated_effective_velocity"] = result["untreated_modified_velocity"] * (
        1.0 + 1.0 / result["untreated_froude"]
    )

    return result


def add_water_jet_properties(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    result = dataset.copy()

    water_area = np.pi * result["water_nozzle_diameter"] ** 2 / 4.0

    result["water_velocity"] = result["water_flow"] / water_area

    result["water_momentum_flux"] = (
        WATER_DENSITY * result["water_flow"] * result["water_velocity"]
    )

    return result


def add_momentum_properties(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    result = dataset.copy()

    result["oil_momentum_flux"] = (
        result["oil_density"] * result["oil_flow"]
        + result["gas_density"] * result["gas_flow"]
    ) * result["untreated_effective_velocity"]

    result["momentum_amplification"] = (
        result["oil_momentum_flux"] + result["water_momentum_flux"]
    ) / result["oil_momentum_flux"]

    result["water_kinetic_power"] = (
        0.5 * WATER_DENSITY * result["water_flow"] * result["water_velocity"] ** 2
    )

    result["oil_kinetic_power"] = (
        0.5
        * (
            result["oil_density"] * result["oil_flow"]
            + result["gas_density"] * result["gas_flow"]
        )
        * result["untreated_effective_velocity"] ** 2
    )

    result["kinetic_power_ratio"] = (
        result["water_kinetic_power"] / result["oil_kinetic_power"]
    )

    return result


def add_derived_properties(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    result = dataset.copy()

    result["dR_measured"] = result["measured_d50"] / result["untreated_d50_measured"]

    result = add_untreated_hydrodynamics(result)

    result = add_water_jet_properties(result)

    result = add_momentum_properties(result)

    return result
