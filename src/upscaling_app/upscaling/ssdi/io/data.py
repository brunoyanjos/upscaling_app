from collections.abc import Sequence

import pandas as pd

from upscaling_app import paths


def load_ssdi_experiments(
    oil_ids: Sequence[int],
    nozzle_diameters: Sequence[float],
    dispersion_kinds: Sequence[str],
) -> pd.DataFrame:
    experiments = pd.read_excel(
        paths.EXPERIMENTS_DATABASE,
    )

    mask = experiments["oil_id"].isin(oil_ids)
    mask &= experiments["nozzle_diameter"].isin(nozzle_diameters)
    mask &= experiments["dispersion_kind"].isin(dispersion_kinds)

    return experiments.loc[mask].copy()


def load_oil_properties() -> pd.DataFrame:
    path = paths.OIL_PROPERTIES_DATABASE

    if not path.exists():
        raise FileNotFoundError(f"Oil properties database not found: {path}")

    oils = pd.read_excel(
        path,
        usecols=[
            "oil_id",
            "oil_name",
            "density",
            "kinematic_viscosity_20c",
            "kinematic_viscosity_40c",
            "kinematic_viscosity_50c",
            "dynamic_viscosity_20c_est",
            "dynamic_viscosity_40c_est",
            "dynamic_viscosity_50c_est",
        ],
    )

    if oils[["oil_id", "oil_name"]].isna().any().any():
        raise ValueError("Missing oil identifiers or names")

    if oils["oil_id"].duplicated().any():
        raise ValueError("Duplicated oil IDs")

    return oils.sort_values("oil_id").reset_index(drop=True)


# Temporary hold: discrepancies with SINTEF report, Table 3.2.
IFT_UNVERIFIED_OILS = frozenset({3015, 4666})


def load_ift_references() -> dict[tuple[int, str], float]:
    """Load laboratory oil-water IFT references in SI (N/m)."""

    data = pd.read_excel(
        paths.EXPERIMENTS_DATABASE,
        usecols=[
            "oil_id",
            "dispersion_kind",
            "dispersion_tag",
            "ift",
        ],
    )

    treatments = {
        "SSDI-C9500": "corexit",
        "SSDI-IBC": "finasol",
    }

    data["treatment"] = data["dispersion_tag"].map(treatments)

    untreated = data["dispersion_kind"].eq("Untreated")
    data.loc[untreated, "treatment"] = "untreated"

    data = data.dropna(subset=["treatment"]).copy()

    if data["ift"].isna().any() or data["ift"].le(0).any():
        raise ValueError("Invalid laboratory IFT values.")

    grouped = (
        data.groupby(["oil_id", "treatment"])["ift"].agg(["min", "max"]).reset_index()
    )

    conflicts = (grouped["max"] - grouped["min"]).abs() > 1e-10

    if conflicts.any():
        raise ValueError("Conflicting IFT values for the same oil and treatment.")

    return {
        (int(row.oil_id), row.treatment): float(row.min)
        for row in grouped.itertuples(index=False)
    }
