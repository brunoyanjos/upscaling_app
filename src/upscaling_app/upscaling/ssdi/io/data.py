from collections.abc import Sequence

import pandas as pd

from upscaling_app import paths


def load_ssdi_experiments(
    oil_ids: Sequence[int],
    nozzle_diameters: Sequence[float],
    dispersion_kinds: Sequence[str],
) -> pd.DataFrame:
    database_path = paths.DATABASE_DIR / "experiments.xlsx"
    df = pd.read_excel(database_path)

    mask = df["oil_id"].isin(oil_ids)
    mask &= df["nozzle_diameter"].isin(nozzle_diameters)
    mask &= df["dispersion_kind"].isin(dispersion_kinds)

    return df.loc[mask].copy()
