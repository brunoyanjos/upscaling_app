from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from upscaling_app.analysis.ssmd.oil_wise.pipeline import (
        SSMDOilWiseResult,
    )


def _print_header(
    title: str,
) -> None:
    print("\n" + "=" * 84)
    print(title)
    print("=" * 84)


def _prepare_comparison_table(
    comparison: pd.DataFrame,
) -> pd.DataFrame:
    table = comparison.copy()

    return table[
        [
            "oil_id",
            "k_global",
            "k_global_std",
            "k_oil",
            "k_oil_std",
            "delta_k",
            "k_ratio",
            "relative_difference_pct",
            "k_global_cv_pct",
            "k_oil_cv_pct",
        ]
    ]


def print_oil_wise_analysis_report(
    result: SSMDOilWiseResult,
) -> None:
    _print_header("SSMD OIL-WISE FACTOR ANALYSIS")

    print(f"\nSSDI source: " f"{result.ssdi_source_version}")

    summary = result.summary.iloc[0]

    print(f"\nNumber of oils                  : " f"{int(summary['n_oils'])}")

    print(f"Mean global factor              : " f"{summary['mean_k_global']:.6f}")

    print(f"Mean oil-wise factor            : " f"{summary['mean_k_oil']:.6f}")

    print(
        f"Mean absolute relative diff.    : "
        f"{summary['mean_abs_relative_difference_pct']:.2f} %"
    )

    print(f"Mean log(k_oil / k_global)      : " f"{summary['mean_log_k_ratio']:.6f}")

    print(f"RMSE log(k_oil / k_global)      : " f"{summary['rmse_log_k_ratio']:.6f}")

    print("\nOil-level comparison")

    table = _prepare_comparison_table(
        result.comparison,
    )

    print(
        "\n"
        + table.to_string(
            index=False,
            formatters={
                "k_global": lambda value: f"{value:.6f}",
                "k_oil": lambda value: f"{value:.6f}",
                "k_std": lambda value: f"{value:.6f}",
                "delta_k": lambda value: f"{value:+.6f}",
                "k_ratio": lambda value: f"{value:.6f}",
                "relative_difference_pct": (lambda value: f"{value:+.2f}"),
                "k_cv_pct": lambda value: f"{value:.2f}",
            },
        )
    )

    print("\nStatus: completed")
    print("=" * 84)
