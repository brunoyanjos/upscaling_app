from __future__ import annotations


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
    save_ssmd_regime_response_plot,
    save_ssmd_gas_effect_plot,
    save_ssmd_momentum_spearman_plot,
    save_ssmd_momentum_response_plot,
    save_ssmd_global_momentum_response_plot,
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
