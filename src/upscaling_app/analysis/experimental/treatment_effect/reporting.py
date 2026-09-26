from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from upscaling_app.analysis.experimental.treatment_effect.pipeline import (
        TreatmentEffectResult,
    )


def print_treatment_effect_report(
    result: TreatmentEffectResult,
) -> None:
    print()
    print("TREATMENT EFFECT")
    print("=" * 72)

    print()
    print("Paired experiments")
    print("-" * 72)
    print(f"Treated experiments : {len(result.effects)}")
    print(f"Oils                : {result.effects['oil_id'].nunique()}")
    print(f"Treatment methods   : " f"{result.effects['dispersion_tag'].nunique()}")

    print()
    print("Treatment summary")
    print("-" * 72)

    summary = result.by_method.copy()

    summary = summary.rename(
        columns={
            "dispersion_tag": "treatment",
            "n_experiments": "experiments",
            "n_oils": "oils",
            "median_reduction_pct": "median_pct",
            "q1_reduction_pct": "q1_pct",
            "q3_reduction_pct": "q3_pct",
            "min_reduction_pct": "min_pct",
            "max_reduction_pct": "max_pct",
        }
    )

    print(
        summary.to_string(
            index=False,
            formatters={
                "median_pct": lambda value: f"{value:.2f}",
                "q1_pct": lambda value: f"{value:.2f}",
                "q3_pct": lambda value: f"{value:.2f}",
                "min_pct": lambda value: f"{value:.2f}",
                "max_pct": lambda value: f"{value:.2f}",
            },
        )
    )

    print()
