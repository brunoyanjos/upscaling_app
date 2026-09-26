from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.experimental.data import load_experiments
from upscaling_app.analysis.experimental.treatment_effect.analysis import (
    build_treatment_effects,
    summarize_treatment_by_method,
    summarize_treatment_by_oil,
)
from upscaling_app.analysis.experimental.treatment_effect.plotting import (
    save_treatment_by_oil_plot,
    save_treatment_reduction_plot,
)
from upscaling_app.analysis.experimental.treatment_effect.reporting import (
    print_treatment_effect_report,
)


@dataclass
class TreatmentEffectResult:
    effects: pd.DataFrame
    by_oil: pd.DataFrame
    by_method: pd.DataFrame


def run_treatment_effect_analysis() -> TreatmentEffectResult:
    data = load_experiments()

    effects = build_treatment_effects(data)

    by_oil = summarize_treatment_by_oil(effects)

    by_method = summarize_treatment_by_method(by_oil)

    return TreatmentEffectResult(
        effects=effects,
        by_oil=by_oil,
        by_method=by_method,
    )


def run_treatment_effect_workflow() -> TreatmentEffectResult:
    result = run_treatment_effect_analysis()

    print_treatment_effect_report(result)

    save_treatment_reduction_plot(
        result.by_method,
        paths.EXPERIMENTAL_TREATMENT_EFFECT_FIGURES_DIR / "d50_reduction_by_method.png",
    )

    save_treatment_by_oil_plot(
        result.by_oil,
        paths.EXPERIMENTAL_TREATMENT_EFFECT_FIGURES_DIR / "d50_reduction_by_oil.png",
    )

    return result
