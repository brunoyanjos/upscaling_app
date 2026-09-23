from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.experimental.data import (
    load_experiments,
    select_experiments,
)
from upscaling_app.analysis.experimental.descriptive import (
    correlation_matrix,
    summarize_by_oil,
    summarize_dataset,
    summarize_regimes,
    summarize_variables,
)
from upscaling_app.analysis.experimental.plotting import (
    save_ssdi_dispersant_comparison_plot,
    save_ssdi_experimental_plots,
    save_ssdi_spearman_plot,
    save_treatment_extremes_plot,
    save_treatment_reduction_summary_plot,
    save_treatment_variability_plot,
    save_water_jet_intensity_plot,
)
from upscaling_app.analysis.experimental.ssdi import (
    build_ssdi_relation_summary,
    build_ssdi_spearman_summary,
    prepare_ssdi_experimental_data,
)
from upscaling_app.analysis.experimental.treatment_effect import (
    build_outlier_diagnostics,
    build_ssdi_dispersant_comparison,
    build_treatment_effects,
    flag_treatment_outliers,
    rank_treatment_effects,
    summarize_treatment_by_method,
    summarize_treatment_effect_by_oil,
    summarize_water_jet_by_fraction,
    summarize_water_jet_monotonicity,
    summarize_water_jet_response,
)

from upscaling_app.analysis.experimental.ssmd import (
    build_ssmd_gas_comparison,
    build_ssmd_spearman_summary,
    prepare_ssmd_experimental_data,
    summarize_ssmd_by_fraction_and_regime,
    summarize_ssmd_by_regime,
    summarize_ssmd_gas_comparison,
    summarize_ssmd_monotonicity,
    summarize_ssmd_monotonicity_by_regime,
)

# ============================================================
# General experimental analysis
# ============================================================


@dataclass
class ExperimentalAnalysisResult:
    data: pd.DataFrame
    dataset_summary: dict[str, object]
    variable_summary: pd.DataFrame
    oil_summary: pd.DataFrame
    regime_summary: pd.DataFrame
    pearson: pd.DataFrame
    spearman: pd.DataFrame


DISPERSION_KINDS = {
    "all": None,
    "untreated": "Untreated",
    "ssdi": "SSDI",
    "ssmd": "SSMD",
}


def run_experimental_analysis(
    kind: str = "all",
) -> ExperimentalAnalysisResult:
    if kind not in DISPERSION_KINDS:
        raise ValueError(f"Unknown dispersion kind: {kind!r}")

    data = load_experiments()

    data = select_experiments(
        data,
        dispersion_kind=DISPERSION_KINDS[kind],
    )

    return ExperimentalAnalysisResult(
        data=data,
        dataset_summary=summarize_dataset(data),
        variable_summary=summarize_variables(data),
        oil_summary=summarize_by_oil(data),
        regime_summary=summarize_regimes(data),
        pearson=correlation_matrix(
            data,
            method="pearson",
        ),
        spearman=correlation_matrix(
            data,
            method="spearman",
        ),
    )


# ============================================================
# SSDI experimental analysis
# ============================================================


@dataclass
class SSDIExperimentalResult:
    pooled: pd.DataFrame
    ssdi_only: pd.DataFrame
    relation_summary: pd.DataFrame
    spearman_summary: pd.DataFrame


def run_ssdi_experimental_analysis() -> SSDIExperimentalResult:
    experiments = load_experiments()

    pooled = prepare_ssdi_experimental_data(
        experiments,
        include_gas=True,
    )

    ssdi_only = pooled.loc[pooled["dispersion_kind"] == "SSDI"].reset_index(drop=True)

    relation_summary = build_ssdi_relation_summary(pooled)

    spearman_summary = build_ssdi_spearman_summary(pooled)

    result = SSDIExperimentalResult(
        pooled=pooled,
        ssdi_only=ssdi_only,
        relation_summary=relation_summary,
        spearman_summary=spearman_summary,
    )

    save_ssdi_experimental_plots(
        result.pooled,
        result.relation_summary,
        paths.EXPERIMENTAL_SSDI_FIGURES_DIR,
    )

    save_ssdi_spearman_plot(
        result.spearman_summary,
        (paths.EXPERIMENTAL_SSDI_FIGURES_DIR / "ssdi_spearman_screening.png"),
    )

    return result


# ============================================================
# Treatment-effect analysis
# ============================================================


@dataclass
class TreatmentEffectResult:
    effects: pd.DataFrame

    by_oil: pd.DataFrame
    by_method: pd.DataFrame

    best: pd.DataFrame
    worst: pd.DataFrame

    flagged_by_oil: pd.DataFrame
    outliers: pd.DataFrame
    outlier_diagnostics: pd.DataFrame

    water_jet_by_oil: pd.DataFrame
    water_jet_by_fraction: pd.DataFrame
    water_jet_monotonicity: pd.DataFrame

    ssdi_comparison: pd.DataFrame


def run_treatment_effect_analysis() -> TreatmentEffectResult:
    experiments = load_experiments()

    effects = build_treatment_effects(experiments)

    by_oil = summarize_treatment_effect_by_oil(effects)

    by_method = summarize_treatment_by_method(by_oil)

    best, worst = rank_treatment_effects(
        by_oil,
        n=5,
    )

    flagged_by_oil = flag_treatment_outliers(by_oil)

    outliers = flagged_by_oil.loc[flagged_by_oil["is_outlier"]].reset_index(drop=True)

    outlier_diagnostics = build_outlier_diagnostics(
        effects,
        flagged_by_oil,
    )

    water_jet_by_oil = summarize_water_jet_response(effects)

    water_jet_by_fraction = summarize_water_jet_by_fraction(water_jet_by_oil)

    water_jet_monotonicity = summarize_water_jet_monotonicity(water_jet_by_oil)

    ssdi_comparison = build_ssdi_dispersant_comparison(by_oil)

    result = TreatmentEffectResult(
        effects=effects,
        by_oil=by_oil,
        by_method=by_method,
        best=best,
        worst=worst,
        flagged_by_oil=flagged_by_oil,
        outliers=outliers,
        outlier_diagnostics=outlier_diagnostics,
        water_jet_by_oil=water_jet_by_oil,
        water_jet_by_fraction=water_jet_by_fraction,
        water_jet_monotonicity=water_jet_monotonicity,
        ssdi_comparison=ssdi_comparison,
    )

    output_dir = paths.EXPERIMENTAL_FIGURES_DIR / "treatment_effect"

    save_treatment_reduction_summary_plot(
        result.by_method,
        (output_dir / "d50_reduction_by_method.png"),
    )

    save_treatment_variability_plot(
        result.flagged_by_oil,
        (output_dir / "d50_reduction_variability.png"),
    )

    save_treatment_extremes_plot(
        result.best,
        result.worst,
        (output_dir / "d50_reduction_extremes.png"),
    )

    save_water_jet_intensity_plot(
        result.water_jet_by_oil,
        result.water_jet_by_fraction,
        (output_dir / "d50_reduction_water_jet_intensity.png"),
    )

    save_ssdi_dispersant_comparison_plot(
        result.ssdi_comparison,
        (output_dir / "d50_reduction_ssdi_comparison.png"),
    )

    return result


# ============================================================
# SSMD experimental analysis
# ============================================================


@dataclass
class SSMDExperimentalResult:
    data: pd.DataFrame

    by_regime: pd.DataFrame
    by_fraction_regime: pd.DataFrame

    spearman_summary: pd.DataFrame

    monotonicity: pd.DataFrame
    monotonicity_by_regime: pd.DataFrame

    gas_comparison: pd.DataFrame
    gas_comparison_summary: pd.DataFrame


def run_ssmd_experimental_analysis() -> SSMDExperimentalResult:
    experiments = load_experiments()

    data = prepare_ssmd_experimental_data(experiments)

    by_regime = summarize_ssmd_by_regime(data)

    by_fraction_regime = summarize_ssmd_by_fraction_and_regime(data)

    spearman_summary = build_ssmd_spearman_summary(data)

    monotonicity = summarize_ssmd_monotonicity(data)

    monotonicity_by_regime = summarize_ssmd_monotonicity_by_regime(monotonicity)

    gas_comparison = build_ssmd_gas_comparison(data)

    gas_comparison_summary = summarize_ssmd_gas_comparison(gas_comparison)

    return SSMDExperimentalResult(
        data=data,
        by_regime=by_regime,
        by_fraction_regime=by_fraction_regime,
        spearman_summary=spearman_summary,
        monotonicity=monotonicity,
        monotonicity_by_regime=monotonicity_by_regime,
        gas_comparison=gas_comparison,
        gas_comparison_summary=(gas_comparison_summary),
    )
