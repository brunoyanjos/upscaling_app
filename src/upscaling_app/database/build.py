import pandas as pd

from upscaling_app import paths
from upscaling_app.database.utils.experiment_id import make_experiment_id
from upscaling_app.database.utils.tags import (
    dispersion_kind,
    normalize_distribution_tag,
)


def build_oil_properties() -> pd.DataFrame:
    df = pd.read_excel(
        paths.OIL_EXTERNAL_PROPERTIES,
        header=[0, 1],
    )

    database = pd.DataFrame(
        {
            "oil_id": df[("SINTEF ID", "Unnamed: 0_level_1")]
            .str.split("-")
            .str[-1]
            .astype(int),
            "oil_name": df[("Petrobras ID", "Unnamed: 1_level_1")],
            "density": df[("Density\n (Kg/L)", "Unnamed: 2_level_1")] * 1000,
            "pour_point": df[("Pour Point \n(°C)", "Unnamed: 3_level_1")],
            "wax_fraction": df[("Wax\n (wght %)", "Unnamed: 4_level_1")] / 100,
            "asphaltene_fraction": df[("Asphaltene \n(wgth %)", "Unnamed: 5_level_1")]
            / 100,
            "viscosity_20c": df[("Viscosity (mPa·s) \nshear rate 10 s⁻¹", "20°C")]
            * 1e-3,
            "viscosity_50c": df[("Viscosity (mPa·s) \nshear rate 10 s⁻¹", "50°C")]
            * 1e-3,
        }
    )

    paths.DATABASE_DIR.mkdir(parents=True, exist_ok=True)

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
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=10)
        df = df.iloc[:60]

        reference_oil = None

        for _, row in df.iterrows():
            tag = str(row.iloc[1])

            if "Untreated" in tag:
                reference_oil = int(tag.split("-")[0])

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
                    "has_gas": float(row.iloc[7]) > 0.0,
                    "ift": float(row.iloc[4]) * 1e-3,
                    "oil_flow": float(row.iloc[6]) / 60000,
                    "gas_flow": float(row.iloc[7]) / 60000,
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
