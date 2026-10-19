import pandas as pd

from upscaling_app import paths
from upscaling_app.database.utils.experiment_id import make_experiment_id
from upscaling_app.database.utils.oil_characterization import (
    build_oil_characterization_table,
    load_oil_reference,
)
from upscaling_app.database.utils.tags import (
    dispersion_kind,
    normalize_distribution_tag,
    water_jet_fraction,
)


def build_oil_properties() -> pd.DataFrame:
    reference = load_oil_reference(paths.OIL_REFERENCE_PATH)

    reference["oil_id"] = reference["oil_id"].astype(int)

    characterization = build_oil_characterization_table(
        oil_reference_path=paths.OIL_REFERENCE_PATH,
        property_directory=paths.OIL_DETAILED_PROPERTIES_DIR,
    )

    reference_ids = set(reference["oil_id"])
    characterization_ids = set(characterization["oil_id"])

    if reference_ids != characterization_ids:
        raise ValueError(
            "Oil IDs do not match between reference and "
            "characterization data. "
            f"Missing: {sorted(reference_ids - characterization_ids)}; "
            f"Unexpected: {sorted(characterization_ids - reference_ids)}"
        )

    database = reference[["oil_id", "oil_name"]].merge(
        characterization,
        on="oil_id",
        how="left",
        validate="one_to_one",
    )

    # Reference density at 15°C, retained for compatibility.
    database.insert(
        2,
        "density",
        database["assay_density_15c"],
    )

    database = database.sort_values("oil_id").reset_index(drop=True)

    # Estimate dynamic viscosity using reference density at 15°C.
    # mu [Pa.s] = rho [kg/m3] * nu [m2/s]
    # Assumption: rho(T) ≈ rho(15°C).
    for temperature in (20, 40, 50):
        database[f"dynamic_viscosity_{temperature}c_est"] = (
            database["assay_density_15c"]
            * database[f"kinematic_viscosity_{temperature}c"]
        )

    paths.DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    database.to_excel(
        paths.OIL_PROPERTIES_DATABASE,
        index=False,
    )

    return database


def build_experiments() -> pd.DataFrame:
    file_path = paths.RAW_DIR / "SINTEF datasheet.xlsx"

    sheets = [
        "Data-3mm",
        "Data-2mm",
        "Data-2mm-gas",
    ]

    records = []

    for sheet_name in sheets:
        raw = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            header=None,
        )

        water_nozzle_diameter = float(raw.iloc[6, 3]) * 1e-3

        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            header=10,
        )

        df = df.iloc[:60]

        reference_oil = None

        for _, row in df.iterrows():
            tag = str(row.iloc[1])

            if "Untreated" in tag:
                reference_oil = int(tag.split("-")[0])

            fraction = water_jet_fraction(tag)

            oil_flow = float(row.iloc[6]) / 60000
            gas_flow = float(row.iloc[7]) / 60000

            water_flow = oil_flow * fraction

            records.append(
                {
                    "experiment_id": make_experiment_id(
                        reference_oil,
                        sheet_name,
                        tag,
                    ),
                    "oil_id": reference_oil,
                    "dispersion_kind": dispersion_kind(tag),
                    "dispersion_tag": tag,
                    "nozzle_diameter": float(row.iloc[5]),
                    "has_gas": gas_flow > 0.0,
                    "ift": float(row.iloc[4]) * 1e-3,
                    "oil_flow": oil_flow,
                    "gas_flow": gas_flow,
                    "water_jet_fraction": fraction,
                    "water_flow": water_flow,
                    "water_nozzle_diameter": (
                        water_nozzle_diameter if fraction > 0.0 else float("nan")
                    ),
                    "oil_viscosity": float(row.iloc[12]) * 1e-3,
                    "gas_density": float(row.iloc[14]),
                    "oil_density": float(row.iloc[15]) * 1e3,
                    "measured_d50": float(row.iloc[3]) * 1e-3,
                    "source_sheet": sheet_name,
                }
            )

    database = pd.DataFrame(records)

    database.to_excel(
        paths.EXPERIMENTS_DATABASE,
        index=False,
    )

    return database


def build_distributions() -> pd.DataFrame:
    records = []

    for file_path in paths.RAW_DIR.glob("*mm all experiments-*.xlsx"):
        oil_id = int(file_path.stem.split("-")[-1])

        nozzle_mm = int(file_path.name.split("mm")[0])
        df = pd.read_excel(file_path)

        diameter = df.iloc[:, 0]

        for column in df.columns[1:]:
            tag, has_gas = normalize_distribution_tag(column, oil_id)

            sheet_name = (
                "Data-2mm-gas" if nozzle_mm == 2 and has_gas else f"Data-{nozzle_mm}mm"
            )

            exp_id = make_experiment_id(
                oil_id,
                sheet_name,
                tag,
            )

            for d, value in zip(diameter, df[column]):
                if pd.isna(d) or pd.isna(value):
                    continue

                records.append(
                    {
                        "experiment_id": exp_id,
                        "droplet_diameter": float(d) * 1e-6,
                        "volume_fraction": float(value) / 100,
                    }
                )

    database = pd.DataFrame(records)

    database.to_excel(
        paths.DISTRIBUTIONS_DATABASE,
        index=False,
    )

    return database


def build_database() -> None:
    paths.DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    oil_properties = build_oil_properties()
    experiments = build_experiments()
    distributions = build_distributions()

    print(f"Oil properties: {len(oil_properties)}")
    print(f"Experiments: {len(experiments)}")
    print(f"Distribution points: {len(distributions)}")
