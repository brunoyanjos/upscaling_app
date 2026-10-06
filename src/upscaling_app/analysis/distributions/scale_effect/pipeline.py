from dataclasses import dataclass

import pandas as pd
from upscaling_app import paths


from upscaling_app.analysis.distributions.parameters.pipeline import (
    run_distribution_parameter_analysis,
)
from upscaling_app.analysis.distributions.scale_effect.analysis import (
    build_gas_effect_pairs,
    build_nozzle_scale_pairs,
    summarize_gas_effect_pairs,
    summarize_nozzle_scale_pairs,
)

from upscaling_app.analysis.distributions.scale_effect.plotting import (
    save_shape_gas_parity_plot,
    save_shape_scale_parity_plot,
)


@dataclass(frozen=True)
class DistributionScaleEffectResult:
    scale_pairs: pd.DataFrame
    scale_summary: pd.DataFrame

    gas_pairs: pd.DataFrame
    gas_summary: pd.DataFrame


def run_distribution_scale_effect_analysis() -> DistributionScaleEffectResult:
    parameter_result = run_distribution_parameter_analysis()

    data = parameter_result.data

    # ---------------------------------------------------------
    # Nozzle-scale effect
    #
    # 2 mm, no gas
    #       ↕
    # 3 mm, no gas
    # ---------------------------------------------------------

    scale_pairs = build_nozzle_scale_pairs(
        data=data,
    )

    scale_summary = summarize_nozzle_scale_pairs(
        pairs=scale_pairs,
    )

    # ---------------------------------------------------------
    # Gas effect
    #
    # 2 mm, no gas
    #       ↕
    # 2 mm, gas
    # ---------------------------------------------------------

    gas_pairs = build_gas_effect_pairs(
        data=data,
    )

    gas_summary = summarize_gas_effect_pairs(
        pairs=gas_pairs,
    )

    return DistributionScaleEffectResult(
        scale_pairs=scale_pairs,
        scale_summary=scale_summary,
        gas_pairs=gas_pairs,
        gas_summary=gas_summary,
    )


def run_distribution_scale_effect_workflow() -> DistributionScaleEffectResult:
    result = run_distribution_scale_effect_analysis()

    save_shape_scale_parity_plot(
        pairs=result.scale_pairs,
        output=(paths.DISTRIBUTION_SCALE_EFFECT_FIGURES_DIR / "shape_scale_parity.png"),
    )

    save_shape_gas_parity_plot(
        pairs=result.gas_pairs,
        output=(paths.DISTRIBUTION_SCALE_EFFECT_FIGURES_DIR / "shape_gas_parity.png"),
    )

    return result
