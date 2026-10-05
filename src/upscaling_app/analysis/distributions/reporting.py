import pandas as pd


def print_distribution_reference_report(
    summary: pd.Series,
    experiment: pd.Series,
) -> None:
    print()
    print("=" * 60)
    print("Experimental Distribution Reference")
    print("=" * 60)

    print(f"Experiment ID : {experiment['experiment_id']}")
    print(f"Oil ID        : {experiment['oil_id']}")
    print(f"Tag           : {experiment['dispersion_tag']}")
    print(f"Nozzle        : " f"{experiment['nozzle_diameter'] * 1e3:.1f} mm")
    print(f"Gas           : {experiment['has_gas']}")

    print()
    print("Distribution")
    print("-" * 60)

    print(f"Volume fraction sum : " f"{summary['volume_fraction_sum']:.6f}")

    print()
    print("Quantiles")
    print("-" * 60)

    print(f"D10 : {summary['d10'] * 1e3:.6f} mm")
    print(f"D50 : {summary['d50'] * 1e3:.6f} mm")
    print(f"D90 : {summary['d90'] * 1e3:.6f} mm")

    print()
    print("Moments")
    print("-" * 60)

    print(f"Mean : " f"{summary['mean_diameter'] * 1e3:.6f} mm")
    print(f"Std  : " f"{summary['std_diameter'] * 1e3:.6f} mm")
    print(f"CV   : {summary['cv']:.6f}")
    print(f"Span : {summary['span']:.6f}")

    print()
    print("D50 consistency")
    print("-" * 60)

    measured_d50 = experiment["measured_d50"]
    distribution_d50 = summary["d50"]

    error_pct = (distribution_d50 - measured_d50) / measured_d50 * 100.0

    print(f"Reported D50     : " f"{measured_d50 * 1e3:.6f} mm")
    print(f"Distribution D50 : " f"{distribution_d50 * 1e3:.6f} mm")
    print(f"Difference       : {error_pct:+.3f} %")

    print("=" * 60)
    print()
