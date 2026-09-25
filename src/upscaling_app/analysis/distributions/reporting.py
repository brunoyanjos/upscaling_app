from upscaling_app.analysis.distributions.pipeline import DistributionAnalysisResult


def print_distribution_analysis_report(
    result: DistributionAnalysisResult,
) -> None:
    comparison = result.d50_comparison.copy()

    comparison["nozzle_mm"] = comparison["nozzle_diameter"] * 1e3

    comparison["measured_d50_mm"] = comparison["measured_d50"] * 1e3

    comparison["distribution_d50_mm"] = comparison["d50"] * 1e3

    comparison["error_pct"] = comparison["d50_relative_error"] * 100.0

    comparison["gas"] = comparison["has_gas"].map(
        {
            True: "yes",
            False: "no",
        }
    )

    comparison["d_peak_mm"] = comparison["d_peak"] * 1e3

    comparison["d_peak_error_pct"] = comparison["d_peak_relative_error"] * 100.0

    comparison = comparison.sort_values(
        [
            "oil_id",
            "nozzle_mm",
            "has_gas",
        ]
    )

    print("\nDISTRIBUTION D50 CHECK")
    print("=" * 90)

    print(
        comparison[
            [
                "oil_id",
                "dispersion_tag",
                "nozzle_mm",
                "gas",
                "measured_d50_mm",
                "distribution_d50_mm",
                "error_pct",
                "d_peak_mm",
                "d_peak_error_pct",
            ]
        ].to_string(
            index=False,
            formatters={
                "nozzle_mm": "{:.1f}".format,
                "measured_d50_mm": "{:.4f}".format,
                "distribution_d50_mm": "{:.4f}".format,
                "error_pct": "{:+.2f}".format,
                "d_peak_mm": "{:.4f}".format,
                "d_peak_error_pct": "{:+.2f}".format,
            },
        )
    )

    suspects = comparison.loc[comparison["d50_relative_error"].abs() > 0.05]

    print("\nSUSPICIOUS D50 CASES")

    print("=" * 120)

    print(
        suspects[
            [
                "oil_id",
                "dispersion_tag",
                "nozzle_mm",
                "gas",
                "measured_d50_mm",
                "distribution_d50_mm",
                "error_pct",
                "d_peak_mm",
                "d_peak_error_pct",
                "source_sheet",
            ]
        ].to_string(
            index=False,
            formatters={
                "nozzle_mm": "{:.1f}".format,
                "measured_d50_mm": "{:.4f}".format,
                "distribution_d50_mm": "{:.4f}".format,
                "error_pct": "{:+.2f}".format,
                "d_peak_mm": "{:.4f}".format,
                "d_peak_error_pct": "{:+.2f}".format,
            },
        )
    )
