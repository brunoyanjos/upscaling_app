from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.experimental.data import load_experiments
from upscaling_app.analysis.experimental.ssmd.analysis import (
    build_ssmd_gas_comparison,
    build_ssmd_momentum_relation_summary,
    prepare_ssmd_experimental_data,
    summarize_ssmd_by_fraction_and_regime,
    summarize_ssmd_by_regime,
    summarize_ssmd_gas_comparison,
    summarize_ssmd_monotonicity,
    summarize_ssmd_monotonicity_by_regime,
)
from upscaling_app.analysis.experimental.ssmd.plotting import (
    save_ssmd_gas_effect_plot,
    save_ssmd_momentum_response_plot,
    save_ssmd_regime_response_plot,
)
from upscaling_app.analysis.experimental.ssmd.reporting import (
    print_ssmd_experimental_report,
)


@dataclass
class SSMDExperimentalResult:
    data: pd.DataFrame

    by_regime: pd.DataFrame
    by_fraction_regime: pd.DataFrame

    monotonicity: pd.DataFrame
    monotonicity_by_regime: pd.DataFrame

    gas_comparison: pd.DataFrame
    gas_comparison_summary: pd.DataFrame

    momentum_relation_summary: pd.DataFrame


def run_ssmd_experimental_analysis() -> SSMDExperimentalResult:
    experiments = load_experiments()

    data = prepare_ssmd_experimental_data(
        experiments,
    )

    by_regime = summarize_ssmd_by_regime(
        data,
    )

    by_fraction_regime = summarize_ssmd_by_fraction_and_regime(
        data,
    )

    monotonicity = summarize_ssmd_monotonicity(
        data,
    )

    monotonicity_by_regime = summarize_ssmd_monotonicity_by_regime(
        monotonicity,
    )

    gas_comparison = build_ssmd_gas_comparison(
        data,
    )

    gas_comparison_summary = summarize_ssmd_gas_comparison(
        gas_comparison,
    )

    momentum_relation_summary = build_ssmd_momentum_relation_summary(
        data,
    )

    return SSMDExperimentalResult(
        data=data,
        by_regime=by_regime,
        by_fraction_regime=by_fraction_regime,
        monotonicity=monotonicity,
        monotonicity_by_regime=monotonicity_by_regime,
        gas_comparison=gas_comparison,
        gas_comparison_summary=gas_comparison_summary,
        momentum_relation_summary=momentum_relation_summary,
    )


def run_ssmd_experimental_workflow() -> SSMDExperimentalResult:
    result = run_ssmd_experimental_analysis()

    print_ssmd_experimental_report(
        result,
    )

    save_ssmd_regime_response_plot(
        result.by_fraction_regime,
        paths.EXPERIMENTAL_SSMD_FIGURES_DIR / "ssmd_response_by_regime.png",
    )

    save_ssmd_gas_effect_plot(
        result.gas_comparison_summary,
        paths.EXPERIMENTAL_SSMD_FIGURES_DIR / "ssmd_gas_effect.png",
    )

    save_ssmd_momentum_response_plot(
        result.data,
        result.momentum_relation_summary,
        paths.EXPERIMENTAL_SSMD_FIGURES_DIR / "ssmd_dR_vs_momentum_amplification.png",
    )

    return result
