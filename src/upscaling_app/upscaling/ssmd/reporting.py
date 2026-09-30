from __future__ import annotations

import pandas as pd


def _print_header(
    title: str,
) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_reference_report(
    predictions: pd.DataFrame,
) -> None:
    _print_header("SSMD SINTEF REFERENCE")

    print(f"\nExperiments        : {len(predictions)}")

    ssdi_source = predictions["ssdi_source_version"].iloc[0]

    print(f"SSDI source        : {ssdi_source}")

    regimes = (
        predictions[
            [
                "nozzle_diameter",
                "has_gas",
                "eta",
                "c_coef",
                "d_coef",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            [
                "nozzle_diameter",
                "has_gas",
            ]
        )
    )

    print("\nSINTEF parameters")

    for row in regimes.itertuples(
        index=False,
    ):
        diameter_mm = row.nozzle_diameter * 1e3

        gas_label = "gas" if row.has_gas else "no gas"

        print(f"\n{diameter_mm:.0f} mm — {gas_label}")

        print(f"  eta              : {row.eta:.6f}")
        print(f"  c                : {row.c_coef:.6f}")
        print(f"  d                : {row.d_coef:.6f}")

    print("\nStatus: completed")
    print("=" * 60)


def print_global_report(
    predictions: pd.DataFrame,
) -> None:
    _print_header("SSMD GLOBAL C,D REGRESSION")

    print(f"\nExperiments        : {len(predictions)}")

    ssdi_source = predictions["ssdi_source_version"].iloc[0]

    print(f"SSDI source        : {ssdi_source}")

    c_values = predictions["c_coef"].dropna().unique()

    d_values = predictions["d_coef"].dropna().unique()

    if len(c_values) != 1 or len(d_values) != 1:
        raise ValueError("Global SSMD predictions must contain one c,d pair.")

    print("\nGlobal coefficients")
    print(f"  c                : {c_values[0]:.6f}")
    print(f"  d                : {d_values[0]:.6f}")

    print("\nStatus: completed")
    print("=" * 60)


def print_oil_wise_report(
    predictions: pd.DataFrame,
) -> None:
    _print_header("SSMD OIL-WISE FACTOR")

    print(f"\nExperiments        : {len(predictions)}")

    ssdi_source = predictions["ssdi_source_version"].iloc[0]

    print(f"SSDI source        : {ssdi_source}")

    coefficients = (
        predictions[
            [
                "oil_id",
                "k_coef",
            ]
        ]
        .drop_duplicates()
        .sort_values("oil_id")
    )

    duplicated = coefficients["oil_id"].duplicated(
        keep=False,
    )

    if duplicated.any():
        raise ValueError("Multiple oil-wise SSMD factors found for the same oil.")

    print("\nOil-wise factors")

    for row in coefficients.itertuples(
        index=False,
    ):
        print(f"  {row.oil_id:<8} " f"k = {row.k_coef:.6f}")

    print("\nStatus: completed")
    print("=" * 60)
