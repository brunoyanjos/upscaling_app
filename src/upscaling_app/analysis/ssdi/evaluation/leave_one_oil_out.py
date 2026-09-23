from dataclasses import dataclass

import jax.numpy as jnp
import numpy as np
import pandas as pd

from upscaling_app.analysis.ssdi.metrics import (
    add_point_metrics,
    calculate_global_metrics,
)
from upscaling_app.upscaling.ssdi.calibration.pipeline import calibrate_ssdi
from upscaling_app.upscaling.ssdi.io.data import load_ssdi_experiments
from upscaling_app.upscaling.ssdi.physics.derived_properties import (
    add_ssdi_physics,
)
from upscaling_app.upscaling.ssdi.prediction import predict_ssdi

ALL_OILS = [
    3014,
    3015,
    3016,
    4661,
    4662,
    4663,
    4664,
    4665,
    4666,
    4667,
]


@dataclass
class LeaveOneOilOutResult:
    folds: pd.DataFrame
    predictions: pd.DataFrame
    global_metrics: dict[str, float]


def run_leave_one_oil_out() -> LeaveOneOilOutResult:
    experiments = load_ssdi_experiments(
        oil_ids=ALL_OILS,
        nozzle_diameters=[2e-3, 3e-3],
        dispersion_kinds=["Untreated", "SSDI"],
    )

    experiments = add_ssdi_physics(experiments)

    fold_rows = []
    prediction_frames = []

    for held_out_oil in ALL_OILS:
        train = experiments.loc[experiments["oil_id"] != held_out_oil].copy()

        test = experiments.loc[experiments["oil_id"] == held_out_oil].copy()

        calibration = calibrate_ssdi(train)

        we_test = jnp.asarray(test["weber"].to_numpy())
        ca_test = jnp.asarray(test["capillary"].to_numpy())

        predictions = predict_ssdi(
            experiments=test,
            we=we_test,
            ca=ca_test,
            a=calibration.a_optimized,
            b=calibration.b_optimized,
            model_version=f"loo_{held_out_oil}",
        )

        predictions["held_out_oil"] = held_out_oil

        predictions = add_point_metrics(predictions)
        metrics = calculate_global_metrics(predictions)

        test_log_mse = float(np.mean(predictions["log_residual"] ** 2))

        fold_rows.append(
            {
                "held_out_oil": held_out_oil,
                "n_train": len(train),
                "n_test": len(test),
                "a": calibration.a_optimized,
                "b": calibration.b_optimized,
                "train_log_mse": calibration.loss,
                "test_log_mse": test_log_mse,
                "r2": metrics["r2"],
                "rmse": metrics["rmse"],
                "mape": metrics["mape"],
                "mean_log_residual": predictions["log_residual"].mean(),
                "std_log_residual": predictions["log_residual"].std(),
            }
        )

        prediction_frames.append(predictions)

    folds = pd.DataFrame(fold_rows)

    pooled_predictions = pd.concat(
        prediction_frames,
        ignore_index=True,
    )

    pooled_metrics = calculate_global_metrics(pooled_predictions)

    global_metrics = {
        "n": len(pooled_predictions),
        "log_mse": float(np.mean(pooled_predictions["log_residual"] ** 2)),
        "r2": pooled_metrics["r2"],
        "rmse": pooled_metrics["rmse"],
        "mape": pooled_metrics["mape"],
        "mean_log_residual": float(pooled_predictions["log_residual"].mean()),
        "std_log_residual": float(pooled_predictions["log_residual"].std()),
    }

    return LeaveOneOilOutResult(
        folds=folds,
        predictions=pooled_predictions,
        global_metrics=global_metrics,
    )
