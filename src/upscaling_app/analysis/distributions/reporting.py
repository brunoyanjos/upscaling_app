import pandas as pd


def report_distribution_analysis(
    *,
    evaluation: pd.DataFrame,
    d50_summary: pd.DataFrame,
    fit_summary: pd.DataFrame,
    selected_cases: pd.DataFrame,
) -> None:
    print()
    print("Distribution analysis")
    print("=" * 60)
    print(f"Experiments evaluated: {len(evaluation)}")

    print()
    print("D50 agreement diagnostics")
    print("-" * 60)

    display = d50_summary.copy()

    for column in (
        "rmse",
        "mae",
        "bias",
        "std_error",
    ):
        display[column] *= 1e3

    display = display.rename(
        columns={
            "rmse": "rmse_mm",
            "mae": "mae_mm",
            "bias": "bias_mm",
            "std_error": "std_error_mm",
        }
    )

    print(
        display.to_string(
            index=False,
            float_format=lambda value: f"{value:.6f}",
        )
    )

    print()
    print("Distribution-fit metrics")
    print("-" * 60)

    print(
        fit_summary.to_string(
            index=False,
            float_format=lambda value: f"{value:.6f}",
        )
    )

    print()
    print("Representative fit cases")
    print("-" * 60)

    columns = [
        "case_group",
        "case_rank",
        "oil_id",
        "dispersion_tag",
        "nozzle_diameter",
        "has_gas",
        "cdf_rmse",
        "cdf_max_error",
    ]

    print(
        selected_cases[columns].to_string(
            index=False,
            float_format=lambda value: f"{value:.6f}",
        )
    )

    print()
