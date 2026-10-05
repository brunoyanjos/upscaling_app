from upscaling_app.analysis.distributions.pipeline import (
    run_distribution_reference_workflow,
)

EXPERIMENT_ID = "4bd20b50-ebe5-5792-ad3a-30e50069d4af"


def main() -> None:
    result = run_distribution_reference_workflow(
        experiment_id=EXPERIMENT_ID,
    )

    print()
    print("Rosin-Rammler — number basis")
    print("-" * 60)

    print(f"k      : " f"{result.number_rr_shape:.6f}")
    print(f"lambda : " f"{result.number_rr_scale * 1e3:.6f} mm")

    print()
    print("Number quantile comparison")
    print("-" * 60)

    print(f"D10 experimental : " f"{result.number_d10 * 1e3:.6f} mm")
    print(f"D10 RR           : " f"{result.number_rr_d10 * 1e3:.6f} mm")

    print(f"D50 experimental : " f"{result.number_d50 * 1e3:.6f} mm")
    print(f"D50 RR           : " f"{result.number_rr_d50 * 1e3:.6f} mm")

    print(f"D90 experimental : " f"{result.number_d90 * 1e3:.6f} mm")
    print(f"D90 RR           : " f"{result.number_rr_d90 * 1e3:.6f} mm")

    print()
    print("Number CDF comparison")
    print("-" * 60)

    print(f"CDF RMSE          : " f"{result.number_cdf_rmse:.6f}")
    print(f"CDF max abs error : " f"{result.number_cdf_max_error:.6f}")


if __name__ == "__main__":
    main()
