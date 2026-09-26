from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from upscaling_app.analysis.experimental.ssmd.pipeline import (
        SSMDExperimentalResult,
    )


REGIME_ORDER = (
    "3 mm — no gas",
    "2 mm — no gas",
    "2 mm — gas",
)


def print_ssmd_experimental_report(
    result: SSMDExperimentalResult,
) -> None:
    print()
    print("SSMD EXPERIMENTAL ANALYSIS")
    print("=" * 72)

    _print_dataset_summary(result)
    _print_regime_summary(result)
    _print_monotonicity_summary(result)
    _print_gas_comparison_summary(result)
    _print_momentum_relation_summary(result)

    print()


def _print_dataset_summary(
    result: SSMDExperimentalResult,
) -> None:
    print()
    print("Dataset")
    print("-" * 72)

    print(f"SSMD experiments : " f"{len(result.data)}")
    print(f"Oils             : " f"{result.data['oil_id'].nunique()}")
    print(f"Regimes          : " f"{result.data['regime'].nunique()}")


def _print_regime_summary(
    result: SSMDExperimentalResult,
) -> None:
    print()
    print("Response by regime")
    print("-" * 72)

    summary = result.by_regime.copy()

    summary["regime"] = summary["regime"].astype(str)

    order = {regime: index for index, regime in enumerate(REGIME_ORDER)}

    summary["_order"] = summary["regime"].map(order).fillna(len(REGIME_ORDER))

    summary = summary.sort_values("_order").drop(columns="_order")

    table = summary.rename(
        columns={
            "n_experiments": "experiments",
            "median_dR": "median_dR",
            "median_reduction_pct": "median_reduction_pct",
        }
    )

    print(
        table[
            [
                "regime",
                "experiments",
                "n_oils",
                "median_dR",
                "median_reduction_pct",
            ]
        ].to_string(
            index=False,
            formatters={
                "median_dR": (lambda value: f"{value:.3f}"),
                "median_reduction_pct": (lambda value: f"{value:.2f}"),
            },
        )
    )


def _print_monotonicity_summary(
    result: SSMDExperimentalResult,
) -> None:
    print()
    print("Water-jet monotonicity")
    print("-" * 72)

    summary = result.monotonicity_by_regime.copy()

    summary["monotonic_pct"] = 100.0 * summary["monotonic_fraction"]

    print(
        summary[
            [
                "regime",
                "n_oils",
                "n_monotonic",
                "monotonic_pct",
            ]
        ].to_string(
            index=False,
            formatters={
                "monotonic_pct": (lambda value: f"{value:.1f}"),
            },
        )
    )


def _print_gas_comparison_summary(
    result: SSMDExperimentalResult,
) -> None:
    print()
    print("2 mm gas vs no-gas comparison")
    print("-" * 72)

    summary = result.gas_comparison_summary.copy()

    table = summary.rename(
        columns={
            "water_jet_pct": "water_jet_pct",
            "median_dR_gas_to_no_gas": ("median_dR_ratio"),
            "median_delta_reduction_pct_points": ("median_delta_pp"),
        }
    )

    print(
        table[
            [
                "water_jet_pct",
                "n_pairs",
                "median_dR_ratio",
                "median_delta_pp",
            ]
        ].to_string(
            index=False,
            formatters={
                "water_jet_pct": (lambda value: f"{value:.0f}"),
                "median_dR_ratio": (lambda value: f"{value:.3f}"),
                "median_delta_pp": (lambda value: f"{value:+.2f}"),
            },
        )
    )


def _print_momentum_relation_summary(
    result: SSMDExperimentalResult,
) -> None:
    print()
    print("Momentum-amplification relation")
    print("-" * 72)

    summary = result.momentum_relation_summary.copy()

    table = summary.rename(
        columns={
            "r2_log": "R2_log",
        }
    )

    print(
        table[
            [
                "regime",
                "n",
                "slope",
                "R2_log",
            ]
        ].to_string(
            index=False,
            formatters={
                "slope": (lambda value: f"{value:+.3f}"),
                "R2_log": (lambda value: f"{value:.3f}"),
            },
        )
    )
