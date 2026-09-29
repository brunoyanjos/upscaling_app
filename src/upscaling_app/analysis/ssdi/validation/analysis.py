import jax.numpy as jnp
import pandas as pd

from upscaling_app.analysis.ssdi.metrics import (
    add_point_metrics,
    calculate_global_metrics,
)
from upscaling_app.analysis.ssdi.performance.analysis import (
    calculate_oil_metrics,
    prepare_performance_results,
)
from upscaling_app.upscaling.ssdi.calibration.pipeline import (
    calibrate_ssdi,
)
from upscaling_app.upscaling.ssdi.datasets import (
    SSDI_DISPERSION_KINDS,
    SSDI_NOZZLE_DIAMETERS,
)
from upscaling_app.upscaling.ssdi.io.data import (
    load_ssdi_experiments,
)
from upscaling_app.upscaling.ssdi.physics.derived_properties import (
    add_ssdi_physics,
)
from upscaling_app.upscaling.ssdi.prediction import (
    predict_ssdi,
)


def _load_population(
    oil_ids: tuple[int, ...],
) -> pd.DataFrame:
    experiments = load_ssdi_experiments(
        oil_ids=oil_ids,
        nozzle_diameters=SSDI_NOZZLE_DIAMETERS,
        dispersion_kinds=SSDI_DISPERSION_KINDS,
    )

    return add_ssdi_physics(
        experiments,
    )


def run_leave_one_oil_out_analysis(
    *,
    oil_ids: tuple[int, ...],
    validation_name: str,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    dict[str, float],
    pd.DataFrame,
]:
    experiments = _load_population(
        oil_ids,
    )

    fold_rows = []
    prediction_frames = []

    for held_out_oil in oil_ids:
        train = experiments.loc[experiments["oil_id"] != held_out_oil].copy()

        test = experiments.loc[experiments["oil_id"] == held_out_oil].copy()

        if test.empty:
            raise ValueError(
                f"No experiments found for held-out oil " f"{held_out_oil}."
            )

        calibration = calibrate_ssdi(
            train,
        )

        we_test = jnp.asarray(test["weber"].to_numpy())

        ca_test = jnp.asarray(test["capillary"].to_numpy())

        predictions = predict_ssdi(
            experiments=test,
            we=we_test,
            ca=ca_test,
            a=calibration.a_optimized,
            b=calibration.b_optimized,
            model_version=validation_name,
        )

        predictions["held_out_oil"] = held_out_oil

        analyzed = add_point_metrics(
            predictions,
        )

        metrics = calculate_global_metrics(
            analyzed,
        )

        fold_rows.append(
            {
                "validation": validation_name,
                "held_out_oil": held_out_oil,
                "train_count": len(train),
                "test_count": len(test),
                "a_initial": calibration.a_initial,
                "b_initial": calibration.b_initial,
                "a_optimized": calibration.a_optimized,
                "b_optimized": calibration.b_optimized,
                "train_log_mse": calibration.loss,
                "test_log_mse": metrics["log_mse"],
                "test_r2": metrics["r2"],
                "test_rmse": metrics["rmse"],
                "test_mape": metrics["mape"],
                "mean_log_residual": float(analyzed["log_residual"].mean()),
                "std_log_residual": float(analyzed["log_residual"].std()),
            }
        )

        prediction_frames.append(predictions)

    folds = pd.DataFrame(fold_rows).sort_values("held_out_oil").reset_index(drop=True)

    predictions = pd.concat(
        prediction_frames,
        ignore_index=True,
    )

    if predictions["experiment_id"].duplicated().any():
        raise ValueError("LOO validation produced duplicate experiment predictions.")

    if len(predictions) != len(experiments):
        raise ValueError(
            "LOO prediction count does not match " "the validation population."
        )

    results = prepare_performance_results(
        predictions,
    )

    global_metrics = calculate_global_metrics(
        results,
    )

    global_metrics["mean_log_residual"] = float(results["log_residual"].mean())

    global_metrics["std_log_residual"] = float(results["log_residual"].std())

    oil_metrics = calculate_oil_metrics(
        results,
    )

    return (
        folds,
        results,
        global_metrics,
        oil_metrics,
    )


def run_excluded_oil_challenge(
    *,
    train_oils: tuple[int, ...],
    challenge_oils: tuple[int, ...],
) -> tuple[
    pd.DataFrame,
    dict[str, float],
    pd.DataFrame,
    pd.DataFrame,
]:
    train = _load_population(
        train_oils,
    )

    challenge = _load_population(
        challenge_oils,
    )

    calibration = calibrate_ssdi(
        train,
    )

    we_test = jnp.asarray(challenge["weber"].to_numpy())

    ca_test = jnp.asarray(challenge["capillary"].to_numpy())

    predictions = predict_ssdi(
        experiments=challenge,
        we=we_test,
        ca=ca_test,
        a=calibration.a_optimized,
        b=calibration.b_optimized,
        model_version="excluded_oil_challenge",
    )

    results = prepare_performance_results(
        predictions,
    )

    global_metrics = calculate_global_metrics(
        results,
    )

    global_metrics["mean_log_residual"] = float(results["log_residual"].mean())

    global_metrics["std_log_residual"] = float(results["log_residual"].std())

    oil_metrics = calculate_oil_metrics(
        results,
    )

    calibration_table = pd.DataFrame(
        [
            {
                "train_oils": ", ".join(map(str, train_oils)),
                "challenge_oils": ", ".join(map(str, challenge_oils)),
                "train_count": len(train),
                "challenge_count": len(challenge),
                "a_initial": calibration.a_initial,
                "b_initial": calibration.b_initial,
                "a_optimized": calibration.a_optimized,
                "b_optimized": calibration.b_optimized,
                "train_log_mse": calibration.loss,
            }
        ]
    )

    return (
        results,
        global_metrics,
        oil_metrics,
        calibration_table,
    )


def build_validation_comparison(
    loo_all: pd.DataFrame,
    loo_retained: pd.DataFrame,
    excluded_challenge: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    definitions = (
        (
            "LOO — all oils",
            "out_of_oil",
            "complete",
            loo_all,
        ),
        (
            "LOO — retained oils",
            "conditional_out_of_oil",
            "retained",
            loo_retained,
        ),
        (
            "Excluded-oil challenge",
            "diagnostic_challenge",
            "excluded",
            excluded_challenge,
        ),
    )

    for (
        label,
        evaluation,
        population,
        table,
    ) in definitions:
        row = table.iloc[0]

        rows.append(
            {
                "validation": label,
                "evaluation": evaluation,
                "population": population,
                "n": int(row["n"]),
                "log_mse": float(row["log_mse"]),
                "r2": float(row["r2"]),
                "rmse": float(row["rmse"]),
                "mape": float(row["mape"]),
                "mean_log_residual": float(row["mean_log_residual"]),
                "std_log_residual": float(row["std_log_residual"]),
            }
        )

    return pd.DataFrame(rows)
