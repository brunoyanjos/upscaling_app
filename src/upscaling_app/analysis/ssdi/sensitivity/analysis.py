import pandas as pd

from upscaling_app.analysis.ssdi.metrics import (
    add_point_metrics,
)
from upscaling_app.analysis.ssdi.outliers import (
    mark_iqr_outliers,
)

RESIDUAL_SENSITIVITY_OILS = (
    3016,
    4665,
)

EXTENDED_SENSITIVITY_OILS = (
    3016,
    4662,
    4665,
)


def select_iqr_population(
    experiments: pd.DataFrame,
    baseline_predictions: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    analyzed = add_point_metrics(
        baseline_predictions,
    )

    analyzed = mark_iqr_outliers(
        analyzed,
    )

    metadata = experiments[
        [
            "experiment_id",
            "oil_id",
        ]
    ].drop_duplicates()

    analyzed = analyzed.merge(
        metadata,
        on="experiment_id",
        how="left",
        validate="one_to_one",
    )

    excluded = analyzed.loc[analyzed["is_outlier"]].copy()

    retained_ids = analyzed.loc[
        ~analyzed["is_outlier"],
        "experiment_id",
    ]

    selected = experiments.loc[experiments["experiment_id"].isin(retained_ids)].copy()

    return (
        selected.reset_index(drop=True),
        excluded.reset_index(drop=True),
    )


def select_oil_exclusion_population(
    experiments: pd.DataFrame,
    oil_ids: tuple[int, ...],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    excluded_mask = experiments["oil_id"].isin(oil_ids)

    selected = experiments.loc[~excluded_mask].copy()

    excluded = experiments.loc[excluded_mask].copy()

    return (
        selected.reset_index(drop=True),
        excluded.reset_index(drop=True),
    )
