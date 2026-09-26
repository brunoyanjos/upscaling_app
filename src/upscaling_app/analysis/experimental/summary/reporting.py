from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from upscaling_app.analysis.experimental.summary.pipeline import (
        ExperimentalSummaryResult,
    )


def _format_nozzle_diameter(value: float) -> str:
    if pd.isna(value):
        return "-"

    return f"{value * 1e3:g}"


def _format_gas(value: bool) -> str:
    return "yes" if value else "no"


def print_experimental_summary_report(
    result: ExperimentalSummaryResult,
) -> None:
    summary = result.dataset_summary

    print()
    print("EXPERIMENTAL SUMMARY")
    print("=" * 60)

    print()
    print("Dataset")
    print("-" * 60)
    print(f"Rows                     : {summary['n_rows']}")
    print(f"Experiments              : {summary['n_experiments']}")
    print(f"Oils                     : {summary['n_oils']}")
    print(f"Duplicate experiment IDs : " f"{summary['n_duplicate_experiment_ids']}")

    print()
    print("Treatment")
    print("-" * 60)
    print(f"Untreated : {summary['n_untreated']}")
    print(f"SSDI      : {summary['n_ssdi']}")
    print(f"SSMD      : {summary['n_ssmd']}")

    print()
    print("Experimental regimes")
    print("-" * 60)

    regimes = result.regime_summary.copy()

    regimes["nozzle_diameter"] = regimes["nozzle_diameter"].map(_format_nozzle_diameter)
    regimes["has_gas"] = regimes["has_gas"].map(_format_gas)

    regimes = regimes.rename(
        columns={
            "dispersion_kind": "kind",
            "nozzle_diameter": "nozzle_mm",
            "has_gas": "gas",
            "n_experiments": "experiments",
            "n_oils": "oils",
        }
    )

    print(
        regimes.to_string(
            index=False,
        )
    )

    print()
    print("Oil coverage")
    print("-" * 60)

    coverage = result.oil_coverage.rename(
        columns={
            "n_experiments": "total",
            "n_untreated": "untreated",
            "n_ssdi": "ssdi",
            "n_ssmd": "ssmd",
        }
    )

    print(
        coverage.to_string(
            index=False,
        )
    )

    print()
    print("Core data completeness")
    print("-" * 60)

    incomplete = result.completeness[result.completeness["n_missing"] > 0].copy()

    if incomplete.empty:
        print("All core fields are complete (100%).")
    else:
        incomplete = incomplete[
            [
                "field",
                "n_present",
                "n_missing",
                "completeness_pct",
            ]
        ]

        print(
            incomplete.to_string(
                index=False,
                formatters={
                    "completeness_pct": lambda value: f"{value:.1f}%",
                },
            )
        )

    print()
