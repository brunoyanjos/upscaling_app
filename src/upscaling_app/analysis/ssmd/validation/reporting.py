from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from upscaling_app.analysis.ssmd.validation.pipeline import (
        SSMDValidationResult,
    )


def print_validation_report(
    result: SSMDValidationResult,
) -> None:
    print()
    print("SSMD leave-one-oil-out validation")
    print("----------------------------------")
    print(f"SSDI source version : {result.ssdi_source_version}")
    print(f"Validation oils     : {len(result.by_oil)}")
    print(f"Predictions         : {len(result.predictions)}")

    summary = result.summary.iloc[0]

    print()
    print("Pooled LOO performance")
    print("----------------------")
    print(f"Log-MSE             : {summary['log_mse']:.6f}")
    print(f"R² log              : {summary['r2_log']:.6f}")
    print(f"RMSE                : {summary['rmse']:.6f}")
    print(f"MAPE                : {summary['mape_pct']:.2f} %")
    print("Mean log residual   : " f"{summary['mean_log_residual']:+.6f}")
    print("Std log residual    : " f"{summary['std_log_residual']:.6f}")

    comparison = result.comparison[
        [
            "evaluation",
            "log_mse",
            "r2_log",
            "rmse",
            "mape_pct",
            "log_mse_change_pct",
        ]
    ].copy()

    comparison["log_mse"] = comparison["log_mse"].map(lambda value: f"{value:.6f}")

    comparison["r2_log"] = comparison["r2_log"].map(lambda value: f"{value:.6f}")

    comparison["rmse"] = comparison["rmse"].map(lambda value: f"{value:.6f}")

    comparison["mape_pct"] = comparison["mape_pct"].map(lambda value: f"{value:.2f}")

    comparison["log_mse_change_pct"] = comparison["log_mse_change_pct"].map(
        lambda value: f"{value:+.2f}"
    )

    print()
    print("In-sample versus LOO")
    print("--------------------")
    print(
        comparison.to_string(
            index=False,
        )
    )

    by_oil = result.by_oil[
        [
            "oil_id",
            "c_coef",
            "d_coef",
            "log_mse",
            "r2_log",
            "mean_log_residual",
            "std_log_residual",
        ]
    ].copy()

    for column in [
        "c_coef",
        "d_coef",
        "log_mse",
        "r2_log",
        "mean_log_residual",
        "std_log_residual",
    ]:
        by_oil[column] = by_oil[column].map(lambda value: f"{value:+.6f}")

    print()
    print("Validation by held-out oil")
    print("--------------------------")
    print(
        by_oil.to_string(
            index=False,
        )
    )
