from __future__ import annotations


def print_oil_wise_comparison(
    result,
) -> None:
    by_oil = result.by_oil.copy()
    overall = result.overall.copy()

    print("\n" + "=" * 110)
    print("SSMD GLOBAL vs OIL-WISE CALIBRATION")
    print("=" * 110)

    print("\nOil-level comparison")
    print(
        by_oil.to_string(
            index=False,
            formatters={
                "k_coef": "{:.6f}".format,
                "log_mse_global": "{:.6f}".format,
                "log_mse_local": "{:.6f}".format,
                "log_mse_reduction_pct": "{:.2f}".format,
                "r2_global": "{:.4f}".format,
                "r2_local": "{:.4f}".format,
                "rmse_global": "{:.4f}".format,
                "rmse_local": "{:.4f}".format,
                "mape_global": "{:.2f}".format,
                "mape_local": "{:.2f}".format,
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
                "rmse",
                "mape",
            ]
        ].to_string(
            index=False,
            formatters={
                "log_mse": "{:.6f}".format,
                "r2": "{:.6f}".format,
                "rmse": "{:.6f}".format,
                "mape": "{:.2f}".format,
            },
        )
    )

    print("\nNote: oil-wise is an in-sample diagnostic with one local factor per oil.")
    print("=" * 110)


def print_performance_comparison(
    result,
) -> None:
    print("\n" + "=" * 100)
    print("SSMD MODEL PERFORMANCE COMPARISON")
    print("=" * 100)

    print("\nOverall performance")
    print(
        result.overall[
            [
                "model",
                "n",
                "log_mse",
                "r2",
                "rmse",
                "mape",
                "mean_log_residual",
            ]
        ].to_string(
            index=False,
            formatters={
                "log_mse": "{:.6f}".format,
                "r2": "{:.6f}".format,
                "rmse": "{:.6f}".format,
                "mape": "{:.2f}".format,
                "mean_log_residual": "{:.6f}".format,
            },
        )
    )

    print("\nPerformance by regime")
    print(
        result.by_regime[
            [
                "model",
                "regime",
                "n",
                "log_mse",
                "r2",
                "rmse",
                "mape",
                "mean_log_residual",
            ]
        ].to_string(
            index=False,
            formatters={
                "log_mse": "{:.6f}".format,
                "r2": "{:.6f}".format,
                "rmse": "{:.6f}".format,
                "mape": "{:.2f}".format,
                "mean_log_residual": "{:.6f}".format,
            },
        )
    )

    print("\nNote: RMSE is dimensionless because the SSMD response is dR.")
    print("=" * 100)
