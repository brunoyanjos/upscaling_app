def print_sensitivity_report(
    *,
    title: str,
    experiment_count: int,
    excluded_count: int,
    a_initial: float,
    b_initial: float,
    a_optimized: float,
    b_optimized: float,
    metrics: dict[str, float],
    excluded_oils: tuple[int, ...] | None = None,
) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)

    print("\nDataset")
    print(f"  Experiments retained : " f"{experiment_count}")
    print(f"  Experiments excluded : " f"{excluded_count}")

    if excluded_oils:
        oil_text = ", ".join(str(oil_id) for oil_id in excluded_oils)

        print(f"  Oils excluded        : " f"{oil_text}")

    print("\nInitial grid search")
    print(f"  A0                   : " f"{a_initial:.6f}")
    print(f"  B0                   : " f"{b_initial:.6f}")

    print("\nOptimized coefficients")
    print(f"  A                    : " f"{a_optimized:.6f}")
    print(f"  B                    : " f"{b_optimized:.6f}")

    print("\nIn-sample metrics")
    print(f"  Log-MSE              : " f"{metrics['log_mse']:.6f}")
    print(f"  R²                   : " f"{metrics['r2']:.6f}")
    print(f"  RMSE                 : " f"{metrics['rmse']:.6e} m")
    print(f"  MAPE                 : " f"{metrics['mape']:.2f} %")

    print("\nEvaluation: in-sample sensitivity analysis")

    print("\nStatus: completed")
    print("=" * 72)
