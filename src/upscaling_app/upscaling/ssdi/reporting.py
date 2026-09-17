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


def print_filtered_report(
    result: SSDIModelResult,
) -> None:
    print_model_report(
        result=result,
        title="SSDI FILTERED CALIBRATION",
    )
