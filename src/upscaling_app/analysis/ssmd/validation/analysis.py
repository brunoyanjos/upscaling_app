from __future__ import annotations

import numpy as np
import pandas as pd

from upscaling_app.analysis.ssmd.metrics import (
    calculate_metrics,
)
from upscaling_app.upscaling.ssmd.calibration.regression import (
    fit_cd_global,
)
from upscaling_app.upscaling.ssmd.prediction import (
    add_global_cd_prediction,
)


def _require_columns(
    data: pd.DataFrame,
    columns: list[str],
    *,
    source: str,
) -> None:
    missing = [column for column in columns if column not in data.columns]

    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def build_leave_one_oil_out_predictions(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        dataset,
        [
            "experiment_id",
            "oil_id",
            "nozzle_diameter",
            "has_gas",
            "water_jet_fraction",
            "momentum_amplification",
            "oil_viscosity",
            "untreated_ift",
            "dR_measured",
        ],
        source="SSMD validation dataset",
    )

    if dataset["oil_id"].isna().any():
        raise ValueError("SSMD validation dataset contains missing oil IDs.")

    oils = sorted(dataset["oil_id"].unique().tolist())

    if len(oils) < 3:
        raise ValueError(
            "Leave-one-oil-out validation requires " "at least three oils."
        )

    folds: list[pd.DataFrame] = []

    for held_out_oil in oils:
        train = dataset.loc[~dataset["oil_id"].eq(held_out_oil)].copy()

        test = dataset.loc[dataset["oil_id"].eq(held_out_oil)].copy()

        train_oils = set(train["oil_id"].unique())

        test_oils = set(test["oil_id"].unique())

        overlap = train_oils & test_oils

        if overlap:
            raise ValueError(
                "Oil leakage detected between "
                "training and test sets: "
                f"{sorted(overlap)}"
            )

        coefficients = fit_cd_global(
            train,
        )

        predicted = add_global_cd_prediction(
            test,
            coefficients,
        )

        predicted["held_out_oil_id"] = held_out_oil

        predicted["n_train"] = len(train)

        predicted["n_test"] = len(test)

        predicted["n_train_oils"] = len(train_oils)

        folds.append(predicted)

    predictions = pd.concat(
        folds,
        ignore_index=True,
    )

    duplicated = predictions["experiment_id"].duplicated(
        keep=False,
    )

    if duplicated.any():
        duplicate_rows = predictions.loc[
            duplicated,
            [
                "experiment_id",
                "oil_id",
                "held_out_oil_id",
            ],
        ]

        raise ValueError(
            "Experiments appear in multiple LOO folds:\n"
            f"{duplicate_rows.to_string(index=False)}"
        )

    if len(predictions) != len(dataset):
        raise ValueError(
            "LOO validation did not produce exactly " "one prediction per experiment."
        )

    mismatch = ~predictions["oil_id"].eq(predictions["held_out_oil_id"])

    if mismatch.any():
        invalid = predictions.loc[
            mismatch,
            [
                "experiment_id",
                "oil_id",
                "held_out_oil_id",
            ],
        ]

        raise ValueError(
            "LOO prediction assigned to an incorrect oil:\n"
            f"{invalid.to_string(index=False)}"
        )

    dR_exp = predictions["dR_measured"].to_numpy(
        dtype=float,
    )

    dR_pred = predictions["dR_pred"].to_numpy(
        dtype=float,
    )

    calculate_metrics(
        dR_exp,
        dR_pred,
    )

    predictions["log_residual"] = np.log(dR_exp / dR_pred)

    return (
        predictions[
            [
                "experiment_id",
                "oil_id",
                "held_out_oil_id",
                "nozzle_diameter",
                "has_gas",
                "water_jet_fraction",
                "n_train",
                "n_test",
                "n_train_oils",
                "c_coef",
                "d_coef",
                "eta",
                "momentum_amplification",
                "dR_measured",
                "dR_pred",
                "log_residual",
            ]
        ]
        .rename(
            columns={
                "dR_measured": "dR_exp",
            }
        )
        .sort_values(
            [
                "oil_id",
                "experiment_id",
            ]
        )
        .reset_index(
            drop=True,
        )
    )


def summarize_leave_one_oil_out_by_oil(
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        predictions,
        [
            "oil_id",
            "held_out_oil_id",
            "n_train",
            "n_test",
            "n_train_oils",
            "c_coef",
            "d_coef",
            "dR_exp",
            "dR_pred",
        ],
        source="SSMD LOO predictions",
    )

    rows: list[dict[str, object]] = []

    for oil_id, group in predictions.groupby(
        "oil_id",
        sort=True,
    ):
        held_out = group["held_out_oil_id"].unique()

        if len(held_out) != 1 or held_out[0] != oil_id:
            raise ValueError(f"Invalid LOO fold for oil {oil_id!r}.")

        c_values = group["c_coef"].unique()

        d_values = group["d_coef"].unique()

        if len(c_values) != 1 or len(d_values) != 1:
            raise ValueError(
                "LOO coefficients are not constant " f"within fold for oil {oil_id!r}."
            )

        metrics = calculate_metrics(
            group["dR_exp"].to_numpy(
                dtype=float,
            ),
            group["dR_pred"].to_numpy(
                dtype=float,
            ),
        )

        rows.append(
            {
                "oil_id": oil_id,
                "n_train": int(group["n_train"].iloc[0]),
                "n_test": int(group["n_test"].iloc[0]),
                "n_train_oils": int(group["n_train_oils"].iloc[0]),
                "c_coef": float(c_values[0]),
                "d_coef": float(d_values[0]),
                **metrics,
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values("oil_id")
        .reset_index(
            drop=True,
        )
    )


def summarize_leave_one_oil_out(
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        predictions,
        [
            "oil_id",
            "dR_exp",
            "dR_pred",
        ],
        source="SSMD LOO predictions",
    )

    metrics = calculate_metrics(
        predictions["dR_exp"].to_numpy(
            dtype=float,
        ),
        predictions["dR_pred"].to_numpy(
            dtype=float,
        ),
    )

    return pd.DataFrame(
        [
            {
                "n_oils": predictions["oil_id"].nunique(),
                **metrics,
            }
        ]
    )


def build_validation_comparison(
    in_sample_predictions: pd.DataFrame,
    loo_predictions: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        in_sample_predictions,
        [
            "experiment_id",
            "dR_exp",
            "dR_pred",
        ],
        source="Global SSMD predictions",
    )

    _require_columns(
        loo_predictions,
        [
            "experiment_id",
            "dR_exp",
            "dR_pred",
        ],
        source="SSMD LOO predictions",
    )

    in_sample_ids = set(in_sample_predictions["experiment_id"])

    loo_ids = set(loo_predictions["experiment_id"])

    if in_sample_ids != loo_ids:
        raise ValueError(
            "In-sample and LOO evaluations require " "identical experiment populations."
        )

    in_sample = calculate_metrics(
        in_sample_predictions["dR_exp"].to_numpy(
            dtype=float,
        ),
        in_sample_predictions["dR_pred"].to_numpy(
            dtype=float,
        ),
    )

    loo = calculate_metrics(
        loo_predictions["dR_exp"].to_numpy(
            dtype=float,
        ),
        loo_predictions["dR_pred"].to_numpy(
            dtype=float,
        ),
    )

    if in_sample["log_mse"] <= 0.0:
        raise ValueError("In-sample Log-MSE must be positive.")

    loo_log_mse_change_pct = 100.0 * (loo["log_mse"] / in_sample["log_mse"] - 1.0)

    return pd.DataFrame(
        [
            {
                "evaluation": "global_in_sample",
                **in_sample,
                "log_mse_change_pct": 0.0,
            },
            {
                "evaluation": "leave_one_oil_out",
                **loo,
                "log_mse_change_pct": (loo_log_mse_change_pct),
            },
        ]
    )
