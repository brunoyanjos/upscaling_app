import pandas as pd

from upscaling_app.upscaling.ssdi.results import (
    BaselineResult,
    SSDIModelResult,
)


def print_model_report(
    result: SSDIModelResult,
    title: str,
) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    print("\nModel")
    print(f"  Version      : {result.model_version}")

    print("\nDataset")
    print(f"  Experiments  : {result.experiment_count}")

    print("\nInitial grid search")
    print(f"  A0           : {result.a_initial:.6f}")
    print(f"  B0           : {result.b_initial:.6f}")

    print("\nOptimized coefficients")
    print(f"  A            : {result.a_optimized:.6f}")
    print(f"  B            : {result.b_optimized:.6f}")
    print(f"  Log-MSE      : {result.loss:.6f}")

    print("\nStatus: completed")
    print("=" * 60)


def print_baseline_report(
    result: BaselineResult,
) -> None:
    model = result.model

    relative_reduction = (
        (result.loss_reference - model.loss) / result.loss_reference * 100.0
    )

    print("\n" + "=" * 60)
    print("SSDI BASELINE CALIBRATION")
    print("=" * 60)

    print("\nDataset")
    print(f"  Experiments        : {model.experiment_count}")

    print("\nInitial grid search")
    print(f"  A0                 : {model.a_initial:.6f}")
    print(f"  B0                 : {model.b_initial:.6f}")

    print("\nOptimized coefficients")
    print(f"  A                  : {model.a_optimized:.6f}")
    print(f"  B                  : {model.b_optimized:.6f}")
    print(f"  Log-MSE            : {model.loss:.6f}")

    print("\nSINTEF reference")
    print(f"  A                  : {result.a_reference:.6f}")
    print(f"  B                  : {result.b_reference:.6f}")
    print(f"  Log-MSE            : {result.loss_reference:.6f}")

    print("\nComparison")
    print(f"  Relative reduction : {relative_reduction:.2f} %")

    print("\nStatus: completed")
    print("=" * 60)


def print_oil_wise_report(
    calibrations: pd.DataFrame,
) -> None:
    if calibrations.empty:
        raise ValueError("Oil-wise calibration results are empty.")

    required_columns = {
        "oil_id",
        "experiment_count",
        "a_optimized",
        "b_optimized",
        "log_mse",
    }

    missing_columns = required_columns.difference(calibrations.columns)

    if missing_columns:
        raise ValueError(
            "Oil-wise calibration results are missing columns: "
            f"{sorted(missing_columns)}."
        )

    data = (
        calibrations[
            [
                "oil_id",
                "experiment_count",
                "a_optimized",
                "b_optimized",
                "log_mse",
            ]
        ]
        .sort_values("oil_id")
        .copy()
    )

    total_experiments = int(data["experiment_count"].sum())

    print("\n" + "=" * 72)
    print("SSDI OIL-WISE CALIBRATION")
    print("=" * 72)

    print("\nDataset")
    print(f"  Oils         : {len(data)}")
    print(f"  Experiments  : {total_experiments}")

    print("\nOptimized coefficients by oil")

    table = data.rename(
        columns={
            "oil_id": "Oil",
            "experiment_count": "n",
            "a_optimized": "A",
            "b_optimized": "B",
            "log_mse": "Log-MSE",
        }
    )

    print(
        table.to_string(
            index=False,
            formatters={
                "Oil": lambda value: f"{int(value)}",
                "n": lambda value: f"{int(value)}",
                "A": lambda value: f"{value:.6f}",
                "B": lambda value: f"{value:.6f}",
                "Log-MSE": lambda value: f"{value:.6f}",
            },
        )
    )

    print("\nCoefficient variability")
    print(f"  A mean       : " f"{data['a_optimized'].mean():.6f}")
    print(f"  A std        : " f"{data['a_optimized'].std():.6f}")
    print(f"  B mean       : " f"{data['b_optimized'].mean():.6f}")
    print(f"  B std        : " f"{data['b_optimized'].std():.6f}")

    print("\nOil-level calibration error")
    print(f"  Mean Log-MSE : " f"{data['log_mse'].mean():.6f}")
    print(f"  Median       : " f"{data['log_mse'].median():.6f}")

    print("\nStatus: completed")
    print("=" * 72)


def print_filtered_report(
    result: SSDIModelResult,
) -> None:
    print_model_report(
        result=result,
        title="SSDI FILTERED CALIBRATION",
    )
