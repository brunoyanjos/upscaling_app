from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

SUMMARY_SHEET = "Summary"


PROPERTY_LABELS = {
    "Density @ 15°C (g/cc)": "assay_density_15c",
    "API Gravity": "api_gravity",
    "UOPK": "uopk",
    "Total Sulphur (% wt)": "sulfur_fraction",
    "Total Nitrogen (ppm)": "total_nitrogen_fraction",
    "Basic Nitrogen (ppm)": "basic_nitrogen_fraction",
    "Total Acid Number (mgKOH/g)": "total_acid_number",
    "Viscosity @ 20°C (cSt)": "kinematic_viscosity_20c",
    "Viscosity @ 40°C (cSt)": "kinematic_viscosity_40c",
    "Viscosity @ 50°C (cSt)": "kinematic_viscosity_50c",
    "Pour Point (°C)": "assay_pour_point",
    "Wax (% wt)": "assay_wax_fraction",
    "C7 Asphaltenes (% wt)": "asphaltenes_c7_fraction",
    "Micro Carbon Residue (% wt)": ("micro_carbon_residue_fraction"),
    "Rams. Carbon Residue (% wt)": ("ramsbottom_carbon_residue_fraction"),
    "Vanadium (ppm)": "vanadium_fraction",
    "Nickel (ppm)": "nickel_fraction",
    "Iron (ppm)": "iron_fraction",
}


WT_PERCENT_FIELDS = {
    "sulfur_fraction",
    "assay_wax_fraction",
    "asphaltenes_c7_fraction",
    "micro_carbon_residue_fraction",
    "ramsbottom_carbon_residue_fraction",
}


PPM_FIELDS = {
    "total_nitrogen_fraction",
    "basic_nitrogen_fraction",
    "vanadium_fraction",
    "nickel_fraction",
    "iron_fraction",
}


KINEMATIC_VISCOSITY_FIELDS = {
    "kinematic_viscosity_20c",
    "kinematic_viscosity_40c",
    "kinematic_viscosity_50c",
}


def _normalize_oil_name(
    value: str,
) -> str:
    value = value.upper()

    value = re.sub(
        r"_REV$",
        "",
        value,
    )

    return re.sub(
        r"[^A-Z0-9]",
        "",
        value,
    )


def _normalize_source_value(
    *,
    field_name: str,
    value: object,
) -> float:
    if pd.isna(value):
        return float("nan")

    if isinstance(
        value,
        str,
    ):
        value = value.strip()

        if value in {
            "",
            "-",
        }:
            return float("nan")

    numeric = float(value)

    if field_name == "assay_density_15c":
        # g/cm³ -> kg/m³
        return numeric * 1000.0

    if field_name in WT_PERCENT_FIELDS:
        # wt % -> mass fraction
        return numeric / 100.0

    if field_name in PPM_FIELDS:
        # ppm -> mass fraction
        return numeric * 1e-6

    if field_name in KINEMATIC_VISCOSITY_FIELDS:
        # cSt -> m²/s
        return numeric * 1e-6

    return numeric


def load_oil_reference(
    path: Path,
) -> pd.DataFrame:
    data = pd.read_csv(
        path,
        dtype={
            "oil_code": str,
            "display_name": str,
        },
    )

    required = {
        "oil_code",
        "display_name",
    }

    missing = required - set(data.columns)

    if missing:
        raise ValueError("Missing columns in oil reference: " f"{sorted(missing)}")

    if data["oil_code"].duplicated().any():
        raise ValueError("Duplicated oil_code in oil reference.")

    data = data.rename(
        columns={
            "oil_code": "oil_id",
            "display_name": "oil_name",
        }
    )

    data["normalized_name"] = data["oil_name"].map(_normalize_oil_name)

    if data["normalized_name"].duplicated().any():
        raise ValueError("Oil names are not unique " "after normalization.")

    return data


def discover_property_files(
    directory: Path,
) -> pd.DataFrame:
    files = sorted(directory.glob("*.xlsx"))

    if not files:
        raise ValueError(
            "No oil characterization spreadsheets " f"found in {directory}"
        )

    rows = []

    for path in files:
        rows.append(
            {
                "assay_source_file": path.name,
                "source_path": path,
                "normalized_name": (_normalize_oil_name(path.stem)),
            }
        )

    data = pd.DataFrame(rows)

    if data["normalized_name"].duplicated().any():
        raise ValueError("Property filenames are not unique " "after normalization.")

    return data


def match_oils_to_property_files(
    oil_reference: pd.DataFrame,
    property_files: pd.DataFrame,
) -> pd.DataFrame:
    matched = oil_reference.merge(
        property_files,
        on="normalized_name",
        how="left",
        validate="one_to_one",
    )

    missing = matched["source_path"].isna()

    if missing.any():
        unresolved = matched.loc[
            missing,
            [
                "oil_id",
                "oil_name",
            ],
        ]

        raise ValueError(
            "No characterization file found for:\n"
            f"{unresolved.to_string(index=False)}"
        )

    unmatched_files = property_files.loc[
        ~property_files["normalized_name"].isin(oil_reference["normalized_name"])
    ]

    if not unmatched_files.empty:
        raise ValueError(
            "Characterization files without " "an oil reference:\n" f"{unmatched_files[
                ['assay_source_file']
            ].to_string(index=False)}"
        )

    return (
        matched[
            [
                "oil_id",
                "oil_name",
                "assay_source_file",
                "source_path",
            ]
        ]
        .sort_values("oil_id")
        .reset_index(drop=True)
    )


def _read_summary_properties(
    path: Path,
) -> dict[str, float]:
    summary = pd.read_excel(
        path,
        sheet_name=SUMMARY_SHEET,
        header=None,
    )

    if summary.shape[1] < 3:
        raise ValueError("Unexpected Summary layout in " f"{path.name}.")

    labels = (
        summary.iloc[
            :,
            1,
        ]
        .astype("string")
        .str.strip()
    )

    values = summary.iloc[
        :,
        2,
    ]

    extracted = {}

    for (
        source_label,
        field_name,
    ) in PROPERTY_LABELS.items():
        match = labels.eq(source_label)

        count = int(match.sum())

        if count == 0:
            raise ValueError(f"Property {source_label!r} " f"not found in {path.name}.")

        if count > 1:
            raise ValueError(
                f"Property {source_label!r} "
                f"appears {count} times "
                f"in {path.name}."
            )

        value = values.loc[match].iloc[0]

        extracted[field_name] = _normalize_source_value(
            field_name=field_name,
            value=value,
        )

    return extracted


def build_oil_characterization_table(
    *,
    oil_reference_path: Path,
    property_directory: Path,
) -> pd.DataFrame:
    oil_reference = load_oil_reference(oil_reference_path)

    property_files = discover_property_files(property_directory)

    mapping = match_oils_to_property_files(
        oil_reference,
        property_files,
    )

    rows = []

    for record in mapping.itertuples(index=False):
        properties = _read_summary_properties(record.source_path)

        rows.append(
            {
                "oil_id": int(record.oil_id),
                "assay_source_file": (record.assay_source_file),
                **properties,
            }
        )

    database = pd.DataFrame(rows)

    if database["oil_id"].duplicated().any():
        raise ValueError("Duplicated oil_id in " "oil characterization table.")

    return database.sort_values("oil_id").reset_index(drop=True)
