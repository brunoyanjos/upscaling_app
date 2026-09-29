from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from upscaling_app.analysis.ssdi.oil_wise.analysis import (
        OilWiseComparisonResult,
    )


def print_oil_wise_comparison_report(
    result: "OilWiseComparisonResult",
) -> None:
    by_oil = result.by_oil.copy()
    overall = result.overall.copy()

    overall["rmse_mm"] = overall["rmse"] * 1e3

    print("\n" + "=" * 100)
    print("SSDI GLOBAL vs OIL-WISE CALIBRATION")
    print("=" * 100)

    print("\nGlobal coefficients")
    print(f"  A            : " f"{result.global_a:.6f}")
    print(f"  B            : " f"{result.global_b:.6f}")

    print("\nOil-level comparison")

    print(
        by_oil.to_string(
            index=False,
            formatters={
                "a_oil_wise": "{:.6f}".format,
                "b_oil_wise": "{:.6f}".format,
                "log_mse_global": "{:.6f}".format,
                "log_mse_oil_wise": "{:.6f}".format,
                "log_mse_reduction_pct": "{:.2f}".format,
            },
        )
    )

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

    print("\nInterpretation")
    print(
        "  Oil-wise coefficients are calibrated and evaluated "
        "on the same oil-specific observations."
    )
    print(
        "  This is an in-sample sensitivity/heterogeneity "
        "diagnostic, not predictive validation."
    )

    print("\nStatus: completed")
    print("=" * 100)
