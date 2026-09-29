import pandas as pd


def print_loo_report(
    *,
    title: str,
    folds: pd.DataFrame,
    global_metrics: dict[str, float],
) -> None:
    table = folds.copy()

    table["test_rmse_mm"] = table["test_rmse"] * 1e3

    print("\n" + "=" * 110)
    print(title)
    print("=" * 110)

    print("\nValidation population")
    print(f"  Folds        : {len(folds)}")
    print(f"  Predictions  : " f"{int(folds['test_count'].sum())}")

    print("\nHeld-out oil performance")

    print(
        table[
            [
                "held_out_oil",
                "train_count",
                "test_count",
                "a_optimized",
                "b_optimized",
                "test_log_mse",
                "test_r2",
                "test_rmse_mm",
                "test_mape",
                "mean_log_residual",
            ]
        ].to_string(
            index=False,
            formatters={
                "a_optimized": "{:.6f}".format,
                "b_optimized": "{:.6f}".format,
                "test_log_mse": "{:.6f}".format,
                "test_r2": "{:.6f}".format,
                "test_rmse_mm": "{:.4f}".format,
                "test_mape": "{:.2f}".format,
                "mean_log_residual": "{:.6f}".format,
            },
        )
    )

    print("\nPooled out-of-oil metrics")
    print(f"  Log-MSE      : " f"{global_metrics['log_mse']:.6f}")
    print(f"  R²           : " f"{global_metrics['r2']:.6f}")
    print(f"  RMSE         : " f"{global_metrics['rmse'] * 1e3:.4f} mm")
    print(f"  MAPE         : " f"{global_metrics['mape']:.2f} %")
    print(f"  Mean log res : " f"{global_metrics['mean_log_residual']:.6f}")
    print(f"  Std log res  : " f"{global_metrics['std_log_residual']:.6f}")

    print("\nEvaluation: predictive validation " "on held-out oils")

    print("\nStatus: completed")
    print("=" * 110)


def print_excluded_challenge_report(
    *,
    calibration: pd.DataFrame,
    oil_metrics: pd.DataFrame,
    global_metrics: dict[str, float],
) -> None:
    calibration_row = calibration.iloc[0]

    table = oil_metrics.copy()

    table["rmse_mm"] = table["rmse"] * 1e3

    print("\n" + "=" * 110)
    print("SSDI EXCLUDED-OIL CHALLENGE")
    print("=" * 110)

    print("\nCalibration population")
    print(f"  Train oils       : " f"{calibration_row['train_oils']}")
    print(f"  Challenge oils   : " f"{calibration_row['challenge_oils']}")
    print(f"  Training n       : " f"{int(calibration_row['train_count'])}")
    print(f"  Challenge n      : " f"{int(calibration_row['challenge_count'])}")

    print("\nCalibration")
    print(f"  A                : " f"{calibration_row['a_optimized']:.6f}")
    print(f"  B                : " f"{calibration_row['b_optimized']:.6f}")
    print(f"  Training Log-MSE : " f"{calibration_row['train_log_mse']:.6f}")

    print("\nChallenge-set performance")

    print(
        table[
            [
                "oil_id",
                "n",
                "log_mse",
                "r2",
                "rmse_mm",
                "mape",
                "mean_log_residual",
            ]
        ].to_string(
            index=False,
            formatters={
                "log_mse": "{:.6f}".format,
                "r2": "{:.6f}".format,
                "rmse_mm": "{:.4f}".format,
                "mape": "{:.2f}".format,
                "mean_log_residual": "{:.6f}".format,
            },
        )
    )

    print("\nPooled challenge metrics")
    print(f"  Log-MSE          : " f"{global_metrics['log_mse']:.6f}")
    print(f"  R²               : " f"{global_metrics['r2']:.6f}")
    print(f"  RMSE             : " f"{global_metrics['rmse'] * 1e3:.4f} mm")
    print(f"  MAPE             : " f"{global_metrics['mape']:.2f} %")

    print(
        "\nEvaluation: diagnostic challenge set; "
        "the excluded oils were selected using prior diagnostics."
    )

    print("\nStatus: completed")
    print("=" * 110)


def print_validation_comparison_report(
    comparison: pd.DataFrame,
) -> None:
    table = comparison.copy()

    table["rmse_mm"] = table["rmse"] * 1e3

    print("\n" + "=" * 110)
    print("SSDI VALIDATION COMPARISON")
    print("=" * 110)

    print(
        "\n"
        + table[
            [
                "validation",
                "evaluation",
                "n",
                "log_mse",
                "r2",
                "rmse_mm",
                "mape",
            ]
        ].to_string(
            index=False,
            formatters={
                "log_mse": "{:.6f}".format,
                "r2": "{:.6f}".format,
                "rmse_mm": "{:.4f}".format,
                "mape": "{:.2f}".format,
            },
        )
    )

    print("\nInterpretation")
    print(
        "  LOO — all oils evaluates out-of-oil "
        "generalization over the complete campaign."
    )
    print(
        "  LOO — retained oils evaluates conditional "
        "out-of-oil generalization within the retained population."
    )
    print(
        "  The excluded-oil challenge is diagnostic, "
        "because those oils were selected using prior results."
    )

    print("\nStatus: completed")
    print("=" * 110)
