import pandas as pd


def print_model_comparison_report(
    comparison: pd.DataFrame,
) -> None:
    table = comparison.copy()

    table["rmse_mm"] = table["rmse"] * 1e3

    print("\n" + "=" * 110)
    print("SSDI MODEL COMPARISON")
    print("=" * 110)

    print(
        "\n"
        + table[
            [
                "model",
                "analysis_type",
                "population",
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
    print("  Baseline and SINTEF reference use the complete dataset.")
    print(
        "  IQR and oil-exclusion results are in-sample "
        "sensitivity analyses on reduced populations."
    )
    print(
        "  Oil-wise calibration uses oil-specific coefficients "
        "and is an in-sample heterogeneity diagnostic."
    )
    print("  Predictive validation is evaluated separately.")

    print("\nStatus: completed")
    print("=" * 110)
