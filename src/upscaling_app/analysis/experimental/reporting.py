from __future__ import annotations

from upscaling_app.analysis.experimental.pipeline import (
    ExperimentalAnalysisResult,
    SSDIExperimentalResult,
    SSMDExperimentalResult,
    TreatmentEffectResult,
)


def _print_separator(
    title: str,
) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# General experimental analysis
# ============================================================


def print_experimental_analysis_report(
    result: ExperimentalAnalysisResult,
) -> None:
    summary = result.dataset_summary

    _print_separator("EXPERIMENTAL DATA ANALYSIS")

    print(f"Experiments : " f"{summary['n_experiments']}")

    print(f"Oils        : " f"{summary['n_oils']}")

    print()
    print("Dispersion kinds")

    print(summary["dispersion_counts"].to_string())

    print()
    print("Gas conditions")

    print(summary["gas_counts"].to_string())

    print()
    print("Nozzle diameters [m]")

    print(summary["nozzle_counts"].to_string())

    _print_separator("DESCRIPTIVE STATISTICS")

    print(
        result.variable_summary.to_string(
            float_format=lambda x: f"{x:.6e}",
        )
    )

    _print_separator("MEASURED D50 BY OIL")

    print(
        result.oil_summary.to_string(
            index=False,
            float_format=lambda x: f"{x:.6e}",
        )
    )

    _print_separator("EXPERIMENTAL REGIMES")

    print(
        result.regime_summary.to_string(
            index=False,
            float_format=lambda x: f"{x:.6e}",
        )
    )

    _print_separator("PEARSON CORRELATION")

    print(
        result.pearson.to_string(
            float_format=lambda x: f"{x:.3f}",
        )
    )

    _print_separator("SPEARMAN CORRELATION")

    print(
        result.spearman.to_string(
            float_format=lambda x: f"{x:.3f}",
        )
    )


# ============================================================
# SSDI experimental analysis
# ============================================================


def print_ssdi_experimental_report(
    result: SSDIExperimentalResult,
) -> None:
    _print_separator("SSDI EXPERIMENTAL ANALYSIS")

    print()
    print("Modified Weber reference coefficient")
    print("B = 0.08")

    print()
    print("Experiments")

    print(f"Pooled    : " f"{len(result.pooled)}")

    print(f"SSDI-only : " f"{len(result.ssdi_only)}")

    _print_separator("SSDI HYDRODYNAMIC SPEARMAN SCREENING")

    print(
        result.spearman_summary[
            [
                "variable",
                "n",
                "spearman_rho",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    _print_separator("LOG-LOG RELATIONS")

    print(
        result.relation_summary[
            [
                "subset",
                "variable",
                "n",
                "slope",
                "r2_log",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )


# ============================================================
# SSMD experimental analysis
# ============================================================


def print_ssmd_experimental_report(
    result: SSMDExperimentalResult,
) -> None:
    _print_separator("SSMD EXPERIMENTAL ANALYSIS")

    print()
    print(f"Experiments : {len(result.data)}")

    print("Oils        : " f"{result.data['oil_id'].nunique()}")

    _print_separator("SSMD RESPONSE BY REGIME")

    print(
        result.by_regime[
            [
                "regime",
                "n",
                "n_oils",
                "median_dR",
                "median_reduction_pct",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    _print_separator("SSMD WATER-JET RESPONSE BY REGIME")

    print(
        result.by_fraction_regime[
            [
                "regime",
                "water_jet_pct",
                "n",
                "median_dR",
                "q1_dR",
                "q3_dR",
                "median_reduction_pct",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    _print_separator("SSMD MONOTONICITY BY REGIME")

    print(
        result.monotonicity_by_regime[
            [
                "regime",
                "n_oils",
                "n_monotonic",
                "monotonic_fraction",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.3f}",
        )
    )

    _print_separator("SSMD 2 MM GAS / NO-GAS COMPARISON")

    print(
        result.gas_comparison_summary[
            [
                "water_jet_pct",
                "n_pairs",
                "median_dR_gas_to_no_gas",
                "median_delta_reduction_pct_points",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    _print_separator("SSMD WATER-JET SPEARMAN SCREENING")

    print(
        result.spearman_summary[
            [
                "regime",
                "n",
                "n_oils",
                "spearman_rho",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    _print_separator("SSMD MOMENTUM-AMPLIFICATION SPEARMAN SCREENING")

    print(
        result.hydrodynamic_spearman[
            [
                "regime",
                "n",
                "n_oils",
                "spearman_rho",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    _print_separator("SSMD OIL-PROPERTY SPEARMAN SCREENING")

    print(
        result.property_spearman[
            [
                "regime",
                "variable",
                "n_oils",
                "spearman_rho",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    _print_separator("SSMD SINTEF PROPERTY-CORRECTION SCREENING")

    print(
        result.property_correction_spearman[
            [
                "regime",
                "n_oils",
                "spearman_rho",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )


# ============================================================
# Treatment-effect analysis
# ============================================================


def print_treatment_effect_report(
    result: TreatmentEffectResult,
) -> None:
    _print_separator("TREATMENT EFFECT ANALYSIS")

    print()
    print("BY METHOD")
    print()

    print(
        result.by_method.to_string(
            index=False,
            float_format=lambda x: f"{x:.2f}",
        )
    )

    print()
    print("TOP 5 RESPONSES")
    print()

    print(
        result.best[
            [
                "oil_id",
                "dispersion_tag",
                "median_reduction_pct",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.2f}",
        )
    )

    print()
    print("BOTTOM 5 RESPONSES")
    print()

    print(
        result.worst[
            [
                "oil_id",
                "dispersion_tag",
                "median_reduction_pct",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.2f}",
        )
    )

    print()
    print("OUTLIERS")
    print()

    if result.outliers.empty:
        print("No outliers detected.")
    else:
        print(
            result.outliers[
                [
                    "oil_id",
                    "dispersion_tag",
                    "median_reduction_pct",
                ]
            ].to_string(
                index=False,
                float_format=lambda x: f"{x:.2f}",
            )
        )

    print()
    print("OUTLIER DIAGNOSTICS")
    print()

    if result.outlier_diagnostics.empty:
        print("No outlier diagnostics available.")
    else:
        print(
            result.outlier_diagnostics.to_string(
                index=False,
                float_format=lambda x: f"{x:.6g}",
            )
        )

    print()
    print("WATER-JET RESPONSE")
    print()

    print(
        result.water_jet_by_fraction.to_string(
            index=False,
            float_format=lambda x: f"{x:.2f}",
        )
    )

    monotonic_count = int(result.water_jet_monotonicity["is_monotonic"].sum())

    total_water_jet_oils = len(result.water_jet_monotonicity)

    print()

    print(
        "Monotonic increase in reduction: "
        f"{monotonic_count}/"
        f"{total_water_jet_oils} oils"
    )

    print()
    print("SSDI DISPERSANT COMPARISON")
    print()

    print(
        result.ssdi_comparison.to_string(
            index=False,
            float_format=lambda x: f"{x:.2f}",
        )
    )

    c9500_count = int(result.ssdi_comparison["c9500_higher_reduction"].sum())

    total_ssdi_oils = len(result.ssdi_comparison)

    print()

    print(
        "C9500 showed higher observed reduction "
        f"in {c9500_count}/"
        f"{total_ssdi_oils} oils."
    )
