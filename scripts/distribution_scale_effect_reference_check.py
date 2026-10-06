import pandas as pd

from upscaling_app.analysis.distributions.scale_effect.pipeline import (
    run_distribution_scale_effect_workflow,
)


def prepare_scale_pairs_for_display(
    pairs: pd.DataFrame,
) -> pd.DataFrame:
    columns = [
        "oil_id",
        "distribution_regime",
        "dispersion_tag",
        "shape_2mm",
        "shape_3mm",
        "shape_delta",
        "shape_ratio",
        "log_shape_ratio",
        "rr_d50_2mm",
        "rr_d50_3mm",
        "rr_d50_ratio",
        "cdf_rmse_2mm",
        "cdf_rmse_3mm",
        "total_variation_2mm",
        "total_variation_3mm",
    ]

    display = pairs[columns].copy()

    display["rr_d50_2mm"] *= 1e3

    display["rr_d50_3mm"] *= 1e3

    return display


def prepare_gas_pairs_for_display(
    pairs: pd.DataFrame,
) -> pd.DataFrame:
    columns = [
        "oil_id",
        "distribution_regime",
        "dispersion_tag",
        "water_jet_fraction",
        "shape_no_gas",
        "shape_gas",
        "shape_delta_gas",
        "shape_ratio_gas",
        "log_shape_ratio_gas",
        "rr_d50_no_gas",
        "rr_d50_gas",
        "rr_d50_ratio_gas",
        "cdf_rmse_no_gas",
        "cdf_rmse_gas",
        "total_variation_no_gas",
        "total_variation_gas",
    ]

    display = pairs[columns].copy()

    display["rr_d50_no_gas"] *= 1e3
    display["rr_d50_gas"] *= 1e3

    display["water_jet_fraction"] = display["water_jet_fraction"].apply(
        lambda value: (f"{value:.0%}" if pd.notna(value) else "-")
    )

    return display


def main() -> None:
    result = run_distribution_scale_effect_workflow()

    # =========================================================
    # NOZZLE-SCALE EFFECT
    #
    # 2 mm, no gas
    #       ↕
    # 3 mm, no gas
    # =========================================================

    print()
    print("Distribution nozzle-scale effect")
    print("-" * 120)

    print(f"Matched 2 mm / 3 mm pairs : " f"{len(result.scale_pairs)}")
    print(f"Unique oils               : " f"{result.scale_pairs['oil_id'].nunique()}")

    # ---------------------------------------------------------
    # Scale pairs by regime
    # ---------------------------------------------------------

    print()
    print("Scale pairs by regime")
    print("-" * 120)

    scale_counts = (
        result.scale_pairs["distribution_regime"]
        .value_counts()
        .rename_axis("regime")
        .reset_index(name="n")
    )

    print(scale_counts.to_string(index=False))

    # ---------------------------------------------------------
    # Scale-effect summary
    # ---------------------------------------------------------

    print()
    print("Scale-effect summary")
    print("-" * 120)

    print(
        result.scale_summary.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )

    # ---------------------------------------------------------
    # Matched scale pairs
    # ---------------------------------------------------------

    print()
    print("Matched 2 mm / 3 mm pairs")
    print("-" * 180)

    scale_display = prepare_scale_pairs_for_display(result.scale_pairs)

    print(
        scale_display.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )

    # ---------------------------------------------------------
    # Scale-effect ranges
    # ---------------------------------------------------------

    print()
    print("Scale-effect ranges")
    print("-" * 120)

    print(
        "k3mm / k2mm : "
        f"{result.scale_pairs['shape_ratio'].min():.6f}"
        " → "
        f"{result.scale_pairs['shape_ratio'].max():.6f}"
    )

    print("median       : " f"{result.scale_pairs['shape_ratio'].median():.6f}")
    print("mean         : " f"{result.scale_pairs['shape_ratio'].mean():.6f}")

    print("median log-ratio : " f"{result.scale_pairs['log_shape_ratio'].median():.6f}")

    # =========================================================
    # GAS EFFECT
    #
    # 2 mm, no gas
    #       ↕
    # 2 mm, gas
    # =========================================================

    print()
    print()
    print("Distribution gas effect")
    print("-" * 120)

    print(f"Matched gas / no-gas pairs : " f"{len(result.gas_pairs)}")

    print(f"Unique oils                 : " f"{result.gas_pairs['oil_id'].nunique()}")

    # ---------------------------------------------------------
    # Gas pairs by regime
    # ---------------------------------------------------------

    print()
    print("Gas pairs by regime")
    print("-" * 120)

    gas_counts = (
        result.gas_pairs["distribution_regime"]
        .value_counts()
        .rename_axis("regime")
        .reset_index(name="n")
    )

    print(gas_counts.to_string(index=False))

    # ---------------------------------------------------------
    # Gas-effect summary
    # ---------------------------------------------------------

    print()
    print("Gas-effect summary")
    print("-" * 120)

    print(
        result.gas_summary.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )

    # ---------------------------------------------------------
    # Matched gas pairs
    # ---------------------------------------------------------

    print()
    print("Matched gas / no-gas pairs")
    print("-" * 180)

    gas_display = prepare_gas_pairs_for_display(result.gas_pairs)

    print(
        gas_display.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )

    # ---------------------------------------------------------
    # Gas-effect ranges
    # ---------------------------------------------------------

    print()
    print("Gas-effect ranges")
    print("-" * 120)

    print(
        "kgas / knogas : "
        f"{result.gas_pairs['shape_ratio_gas'].min():.6f}"
        " → "
        f"{result.gas_pairs['shape_ratio_gas'].max():.6f}"
    )

    print("median        : " f"{result.gas_pairs['shape_ratio_gas'].median():.6f}")
    print("mean          : " f"{result.gas_pairs['shape_ratio_gas'].mean():.6f}")

    print(
        "median log-ratio : " f"{result.gas_pairs['log_shape_ratio_gas'].median():.6f}"
    )


if __name__ == "__main__":
    main()
