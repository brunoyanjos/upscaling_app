from __future__ import annotations

import pandas as pd

from upscaling_app import paths


def load_experiments() -> pd.DataFrame:
    return pd.read_excel(paths.EXPERIMENTS_DATABASE)


def filter_by_dispersion(
    data: pd.DataFrame,
    dispersion_kind: str | None = None,
) -> pd.DataFrame:
    if dispersion_kind is None:
        return data.copy()

    selected = data.loc[data["dispersion_kind"] == dispersion_kind].copy()

    return selected.reset_index(drop=True)
