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
    print(f"  Log-MSE      : {metrics['log_mse']:.6f}")
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


def print_oil_wise_comparison(
    result,
) -> None:
    by_oil = result.by_oil.copy()
    overall = result.overall.copy()

    print("\n" + "=" * 100)
    print("SSDI GLOBAL vs OIL-WISE CALIBRATION")
    print("=" * 100)

    print("\nOil-level comparison")

    print(
        by_oil.to_string(
            index=False,
            formatters={
                "a_local": "{:.6f}".format,
                "b_local": "{:.6f}".format,
                "log_mse_global": "{:.6f}".format,
                "log_mse_local": "{:.6f}".format,
                "log_mse_reduction_pct": "{:.2f}".format,
            },
        )
    )

    overall["rmse_mm"] = overall["rmse"] * 1e3

    print("\nOverall performance")

    print(
        overall[
            [
                "model",
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

    print("\nInterpretation:")
    print("  oil_wise is an in-sample calibration " "with oil-specific A and B.")
    print("  It is not an out-of-oil predictive validation.")

    print("\nStatus: completed")
    print("=" * 100)


def print_ssdi_performance_comparison(
    result,
) -> None:
    overall = result.overall.copy()
    by_gas = result.by_gas.copy()

    overall["rmse_mm"] = overall["rmse"] * 1e3

    by_gas["rmse_mm"] = by_gas["rmse"] * 1e3

    by_gas["condition"] = by_gas["has_gas"].map(
        {
            False: "no gas",
            True: "gas",
        }
    )

    print("\n" + "=" * 95)
    print("SSDI MODEL PERFORMANCE COMPARISON")
    print("=" * 95)

    print("\nOverall performance")

    print(
        overall[
            [
                "model",
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

    print("\n2 mm performance by gas condition")

    print(
        by_gas[
            [
                "model",
                "condition",
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

    print("\nNotes:")
    print("  Gas comparison is restricted to the 2 mm nozzle.")
    print("  Oil-wise results are in-sample and use oil-specific A and B.")

    print("\nStatus: completed")
    print("=" * 95)
