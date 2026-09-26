from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from upscaling_app.analysis.experimental.ssdi.pipeline import (
        SSDIExperimentalResult,
    )


def print_ssdi_experimental_report(
    result: SSDIExperimentalResult,
) -> None:
    print()
    print("SSDI EXPERIMENTAL ANALYSIS")
    print("=" * 72)

    _print_dataset_summary(result)
    _print_dispersant_comparison(result)
    _print_spearman_summary(result)
    _print_relation_summary(result)

    print()


def _print_dataset_summary(
    result: SSDIExperimentalResult,
) -> None:
    print()
    print("Dataset")
    print("-" * 72)

    print(f"Untreated + SSDI experiments : {len(result.data)}")
    print(f"SSDI experiments             : {len(result.ssdi_only)}")
    print(f"Oils                         : {result.data['oil_id'].nunique()}")
    print(f"Gas cases                    : " f"{int(result.data['has_gas'].sum())}")
    print(f"No-gas cases                 : " f"{int((~result.data['has_gas']).sum())}")


def _print_dispersant_comparison(
    result: SSDIExperimentalResult,
) -> None:
    print()
    print("C9500 vs IBC")
    print("-" * 72)

    comparison = result.dispersant_comparison.copy()

    n_oils = len(comparison)

    c9500_higher = (comparison["delta_pct_points"] > 0.0).sum()

    print(f"Oils compared           : {n_oils}")
    print(f"C9500 higher reduction  : {c9500_higher} / {n_oils}")
    print()

    table = comparison.rename(
        columns={
            "c9500_reduction_pct": "c9500_pct",
            "ibc_reduction_pct": "ibc_pct",
            "delta_pct_points": "delta_pp",
        }
    )

    print(
        table.to_string(
            index=False,
            formatters={
                "c9500_pct": lambda value: f"{value:.2f}",
                "ibc_pct": lambda value: f"{value:.2f}",
                "delta_pp": lambda value: f"{value:+.2f}",
            },
        )
    )


def _print_spearman_summary(
    result: SSDIExperimentalResult,
) -> None:
    print()
    print("Hydrodynamic Spearman screening")
    print("-" * 72)

    summary = result.spearman_summary.copy()

    for subset in (
        "pooled",
        "ssdi_only",
    ):
        data = summary.loc[summary["subset"] == subset].copy()

        print()
        print(subset.replace("_", " ").title())

        data = data[
            [
                "variable",
                "n",
                "spearman_rho",
            ]
        ]

        print(
            data.to_string(
                index=False,
                formatters={
                    "spearman_rho": lambda value: f"{value:+.3f}",
                },
            )
        )


def _print_relation_summary(
    result: SSDIExperimentalResult,
) -> None:
    print()
    print("Log-log relations")
    print("-" * 72)

    summary = result.relation_summary.copy()

    summary = summary.rename(
        columns={
            "r2_log": "R2_log",
        }
    )

    print(
        summary[
            [
                "subset",
                "variable",
                "n",
                "slope",
                "R2_log",
            ]
        ].to_string(
            index=False,
            formatters={
                "slope": lambda value: f"{value:+.3f}",
                "R2_log": lambda value: f"{value:.3f}",
            },
        )
    )
