import pandas as pd

import upscaling_app.paths as paths

from upscaling_app.analysis.distributions.parameters.pipeline import (
    run_distribution_parameter_workflow,
)

SUMMARY_COLUMNS = [
    "mean",
    "std",
    "min",
    "q25",
    "median",
    "q75",
    "max",
]


def prepare_summary_for_display(
    summary: pd.DataFrame,
) -> pd.DataFrame:
    display = summary.copy()

    diameter_parameters = display["parameter"].isin(
        [
            "scale",
            "rr_d50",
        ]
    )

    display.loc[
        diameter_parameters,
        SUMMARY_COLUMNS,
    ] *= 1e3

    display["unit"] = "-"

    display.loc[
        display["parameter"] == "scale",
        "unit",
    ] = "mm"

    display.loc[
        display["parameter"] == "rr_d50",
        "unit",
    ] = "mm"

    return display[
        [
            "regime",
            "parameter",
            "unit",
            "n",
            *SUMMARY_COLUMNS,
        ]
    ]


def prepare_data_for_display(
    data: pd.DataFrame,
) -> pd.DataFrame:
    columns = [
        "experiment_id",
        "oil_id",
        "distribution_regime",
        "dispersion_tag",
        "nozzle_diameter",
        "has_gas",
        "measured_d50",
        "shape",
        "scale",
        "rr_d50",
        "scale_to_rr_d50",
    ]

    display = data[columns].copy()

    display["nozzle_diameter"] *= 1e3

    display["measured_d50"] *= 1e3

    display["scale"] *= 1e3

    display["rr_d50"] *= 1e3

    return display


def main() -> None:
    result = run_distribution_parameter_workflow()

    # ---------------------------------------------------------
    # Integrity
    # ---------------------------------------------------------

    print()
    print("Distribution parameter analysis")
    print("-" * 120)

    print(f"Parameter sets : " f"{len(result.data)}")

    print(f"Unique oils    : " f"{result.data['oil_id'].nunique()}")

    print(f"Regimes        : " f"{result.data['distribution_regime'].nunique()}")

    # ---------------------------------------------------------
    # Regime counts
    # ---------------------------------------------------------

    print()
    print("Experiments by regime")
    print("-" * 120)

    regime_counts = (
        result.data["distribution_regime"]
        .value_counts()
        .rename_axis("regime")
        .reset_index(name="n")
    )

    print(regime_counts.to_string(index=False))

    # ---------------------------------------------------------
    # Parameter summary
    # ---------------------------------------------------------

    print()
    print("Distribution parameter summary")
    print("-" * 120)

    summary_display = prepare_summary_for_display(result.summary)

    print(
        summary_display.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )

    # ---------------------------------------------------------
    # First fitted parameter sets
    # ---------------------------------------------------------

    print()
    print("First fitted parameter sets")
    print("-" * 120)

    data_display = prepare_data_for_display(result.data)

    print(
        data_display.head(10).to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )

    # ---------------------------------------------------------
    # Parameter ranges
    # ---------------------------------------------------------

    print()
    print("Shape extremes and fit quality")
    print("-" * 140)

    extremes = result.shape_extremes.copy()

    extremes["nozzle_diameter"] *= 1e3

    extremes["scale"] *= 1e3

    extremes["rr_d50"] *= 1e3

    print(
        extremes.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )

    print()
    print("Global parameter ranges")
    print("-" * 120)

    shape = result.data["shape"]

    scale = result.data["scale"] * 1e3

    rr_d50 = result.data["rr_d50"] * 1e3

    ratio = result.data["scale_to_rr_d50"]

    print(f"shape     : " f"{shape.min():.6f}" f" → " f"{shape.max():.6f}")

    print(f"scale     : " f"{scale.min():.6f}" f" → " f"{scale.max():.6f} mm")

    print(f"RR D50    : " f"{rr_d50.min():.6f}" f" → " f"{rr_d50.max():.6f} mm")

    print(f"lambda/D50: " f"{ratio.min():.6f}" f" → " f"{ratio.max():.6f}")

    print()
    print("Figures")
    print("-" * 120)

    print(
        "Shape by regime     : "
        f"{paths.DISTRIBUTION_PARAMETER_FIGURES_DIR / 'shape_by_regime.png'}"
    )

    print(
        "Shape vs fit quality: "
        f"{paths.DISTRIBUTION_PARAMETER_FIGURES_DIR / 'shape_vs_fit_quality.png'}"
    )


if __name__ == "__main__":
    main()
