import pandas as pd


def print_ssdi_analysis_report(
    results: pd.DataFrame,
    metrics: dict[str, float],
    model_version: str,
) -> None:
    outlier_count = int(results["is_outlier"].sum())

    print("\n" + "=" * 60)
    print("SSDI MODEL ANALYSIS")
    print("=" * 60)

    print("\nModel")
    print(f"  Version      : {model_version}")

    print("\nDataset")
    print(f"  Experiments  : {len(results)}")
    print(f"  Outliers     : {outlier_count}")

    print("\nGlobal metrics")
    print(f"  R²           : {metrics['r2']:.6f}")
    print(f"  RMSE         : {metrics['rmse']:.6e} m")
    print(f"  MAPE         : {metrics['mape']:.2f} %")

    print("\nStatus: completed")
    print("=" * 60)


def print_model_comparison(
    comparison: pd.DataFrame,
) -> None:
    print("\n" + "=" * 60)
    print("SSDI MODEL COMPARISON")
    print("=" * 60)

    print(
        comparison.to_string(
            index=False,
            formatters={
                "a": "{:.6f}".format,
                "b": "{:.6f}".format,
                "log_mse": "{:.6f}".format,
                "r2": "{:.6f}".format,
                "rmse": "{:.6e}".format,
                "mape": "{:.2f}".format,
            },
        )
    )

    print("\nStatus: completed")
    print("=" * 60)


def print_leave_one_oil_out_report(
    result,
) -> None:
    metrics = result.global_metrics

    print("\n" + "=" * 60)
    print("SSDI LEAVE-ONE-OIL-OUT VALIDATION")
    print("=" * 60)

    print(f"Folds       : {len(result.folds)}")
    print(f"Predictions : {metrics['n']}")

    print("\nGlobal validation metrics")
    print(f"Log-MSE     : {metrics['log_mse']:.6f}")
    print(f"R²          : {metrics['r2']:.6f}")
    print(f"RMSE        : {metrics['rmse']:.6e} m")
    print(f"MAPE        : {metrics['mape']:.2f} %")
    print(f"Mean log res: " f"{metrics['mean_log_residual']:.6f}")
    print(f"Std log res : " f"{metrics['std_log_residual']:.6f}")

    print("\nStatus: completed")
    print("=" * 60)


def print_evaluation_comparison(
    comparison: pd.DataFrame,
) -> None:
    print("\n" + "=" * 80)
    print("SSDI EVALUATION COMPARISON")
    print("=" * 80)

    print(
        comparison.to_string(
            index=False,
            formatters={
                "log_mse": "{:.6f}".format,
                "r2": "{:.6f}".format,
                "rmse": "{:.6e}".format,
                "mape": "{:.2f}".format,
            },
        )
    )

    print("\nEvaluation:")
    print("  in_sample  = evaluated on calibration data")
    print("  out_of_oil = held-out oil not used in calibration")

    print("=" * 80)
