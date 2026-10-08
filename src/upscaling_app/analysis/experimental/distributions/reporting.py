import pandas as pd


def print_distribution_consistency_report(
    comparison: pd.DataFrame,
) -> None:
    display = comparison.copy()

    display["measured_d50_mm"] = display["measured_d50"] * 1e3
    display["reconstructed_d50_mm"] = display["d50"] * 1e3
    display["d50_relative_error_pct"] = display["d50_relative_error"] * 100.0
    display["percentile_error_pct"] = display["percentile_error"] * 100.0
    display["absolute_error"] = display["d50_relative_error"].abs()

    display = display.sort_values("absolute_error", ascending=False)

    print()
    print("Experimental distribution consistency")
    print("-" * 72)

    print(f"Experiments analysed : " f"{len(display)}")

    print()
    print("Largest D50 discrepancies")
    print("-" * 72)

    columns = [
        "oil_id",
        "dispersion_tag",
        "measured_d50_mm",
        "reconstructed_d50_mm",
        "d50_relative_error_pct",
        "reported_percentile",
    ]

    print(
        display[columns]
        .head(10)
        .to_string(index=False, float_format=lambda x: (f"{x:.3f}"))
    )
