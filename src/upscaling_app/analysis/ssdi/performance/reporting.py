from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from upscaling_app.analysis.ssdi.performance.pipeline import (
        SSDIPerformanceResult,
    )


def print_performance_report(
    result: "SSDIPerformanceResult",
) -> None:
    metrics = result.global_metrics

    print("\n" + "=" * 72)
    print("SSDI MODEL PERFORMANCE")
    print("=" * 72)

    print("\nModel")
    print(f"  Name         : " f"{result.model_label}")
    print(f"  Version      : " f"{result.model_version}")

    print("\nDataset")
    print(f"  Experiments  : " f"{len(result.results)}")
    print(f"  Outliers     : " f"{int(result.results['is_outlier'].sum())}")

    print("\nGlobal metrics")
    print(f"  Log-MSE      : " f"{metrics['log_mse']:.6f}")
    print(f"  R²           : " f"{metrics['r2']:.6f}")
    print(f"  RMSE         : " f"{metrics['rmse'] * 1e3:.4f} mm")
    print(f"  MAPE         : " f"{metrics['mape']:.2f} %")

    oil_table = result.oil_metrics.copy()

    oil_table["rmse_mm"] = oil_table["rmse"] * 1e3

    print("\nOil-level diagnostics")

    print(
        oil_table[
            [
                "oil_id",
                "n",
                "log_mse",
                "r2",
                "rmse_mm",
                "mape",
                "mean_log_residual",
                "outlier_count",
            ]
        ].to_string(
            index=False,
            formatters={
                "log_mse": "{:.6f}".format,
                "r2": "{:.6f}".format,
                "rmse_mm": "{:.4f}".format,
                "mape": "{:.2f}".format,
                "mean_log_residual": ("{:.6f}".format),
            },
        )
    )

    print("\nStatus: completed")
    print("=" * 72)
