from pathlib import Path
from utils.paths import RAW_DB_PATH, OIL_REFERENCE_PATH, DATABASE_PATH

import pandas as pd
import numpy as np


def dispersion_kind(tag: str) -> str:
    if "Untreated" in tag:
        return "Untereated"

    if "SSDI" in tag:
        return "SSDI"

    return "SSMD"


def dispersion_property(tag: str) -> str:
    if "Untreated" in tag:
        return "Untreated"

    if "SSDI" in tag:
        return tag.split("-")[1]

    return tag.split("-")[1][0:-1]


oil_name_ds = pd.read_csv(Path(OIL_REFERENCE_PATH) / "oils.csv")

n_values = oil_name_ds.shape[0]

oil_code = oil_name_ds["oil_code"].to_numpy()
display_name = oil_name_ds["display_name"].to_numpy()

oil_dict = {}

for code, name in zip(oil_code, display_name):
    oil_dict[int(code)] = name

file_path = Path(RAW_DB_PATH) / "SINTEF datasheet.xlsx"

three_mm_data = pd.read_excel(file_path, sheet_name="Data-3mm", header=10)
three_mm_data = three_mm_data.rename(columns={three_mm_data.columns[1]: "Tag"})

two_mm_data = pd.read_excel(file_path, sheet_name="Data-2mm", header=10)
two_mm_data = two_mm_data.rename(columns={two_mm_data.columns[1]: "Tag"})

two_mm_gas_data = pd.read_excel(file_path, sheet_name="Data-2mm-gas", header=10)
two_mm_gas_data = two_mm_gas_data.rename(columns={two_mm_gas_data.columns[1]: "Tag"})

registros = []

reference_oil = ""

for index, row in three_mm_data.iterrows():
    if index < 60:
        tag = str(row["Tag"])
        data = {}

        if "Untreated" in tag:
            reference_oil = tag.split("-")[0]

        data["reference_number"] = reference_oil
        data["dispersion_kind"] = dispersion_kind(tag)
        data["dispesion_property"] = dispersion_property(tag)
        data["nozzle_diameter"] = float(row.iloc[5])
        data["IFT"] = float(row.iloc[4]) * 1e-3
        data["oil_flow"] = float(row.iloc[6]) / 60000
        data["gas_flow"] = float(row.iloc[7]) / 60000
        data["oil_visc"] = float(row.iloc[12]) * 1e-3
        data["gas_density"] = float(row.iloc[14])
        data["oil_density"] = float(row.iloc[15]) * 1e3

        registros.append(data)


for index, row in two_mm_data.iterrows():
    if index < 60:
        tag = str(row["Tag"])
        data = {}

        if "Untreated" in tag:
            reference_oil = tag.split("-")[0]

for index, row in two_mm_gas_data.iterrows():
    if index < 60:
        tag = str(row["Tag"])
        data = {}

        if "Untreated" in tag:
            reference_oil = tag.split("-")[0]

database_file_path = Path(DATABASE_PATH) / "database.xlsx"

database = pd.DataFrame(registros)
database.to_excel(database_file_path, index=False)
