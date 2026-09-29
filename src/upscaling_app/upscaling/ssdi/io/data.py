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
