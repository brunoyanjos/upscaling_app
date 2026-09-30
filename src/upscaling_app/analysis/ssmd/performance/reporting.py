from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from upscaling_app.analysis.ssmd.performance.pipeline import (
        SSMDPerformanceResult,
    )


MODEL_LABELS = {
    "sintef_reference": "SINTEF reference",
    "global_cd": "Global c,d",
}


def _print_header(
    title: str,
) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def _prepare_report_table(
    comparison: pd.DataFrame,
) -> pd.DataFrame:
    table = comparison.copy()

    table["model"] = (
        table["ssmd_model_version"]
        .map(MODEL_LABELS)
        .fillna(table["ssmd_model_version"])
    )

    table["target"] = table["evaluation_target"].map(
        {
            "dR": "dR",
            "d50": "d50",
        }
    )

    table["rmse_display"] = table["rmse"]

    d50_mask = table["evaluation_target"].eq("d50")

    table.loc[
        d50_mask,
        "rmse_display",
    ] *= 1e3

    table["rmse_unit"] = "[-]"

    table.loc[
        d50_mask,
        "rmse_unit",
    ] = "mm"

    return table[
        [
            "model",
            "target",
            "n",
            "log_mse",
            "r2_log",
            "rmse_display",
            "rmse_unit",
            "mape_pct",
            "mean_log_residual",
            "std_log_residual",
        ]
    ]


def print_performance_report(
    result: SSMDPerformanceResult,
) -> None:
    _print_header("SSMD PERFORMANCE")

    print(f"\nSSDI source: " f"{result.ssdi_source_version}")

    table = _prepare_report_table(
        result.comparison,
    )

    for target in [
        "dR",
        "d50",
    ]:
        subset = table.loc[table["target"].eq(target)]

        print(f"\n{target} performance")

        for row in subset.itertuples(
            index=False,
        ):
            print(f"\n{row.model}")

            print(f"  n                 : " f"{row.n}")

            print(f"  Log-MSE           : " f"{row.log_mse:.6f}")

            print(f"  R² log            : " f"{row.r2_log:.6f}")

            print(
                f"  RMSE              : " f"{row.rmse_display:.6f} " f"{row.rmse_unit}"
            )

            print(f"  MAPE              : " f"{row.mape_pct:.2f} %")

            print(f"  Mean log residual : " f"{row.mean_log_residual:.6f}")

            print(f"  Std log residual  : " f"{row.std_log_residual:.6f}")

    print("\nStatus: completed")
    print("=" * 72)
