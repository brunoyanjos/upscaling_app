from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.experimental.data import load_experiments
from upscaling_app.analysis.experimental.ssdi.analysis import (
    build_ssdi_dispersant_comparison,
    build_ssdi_relation_summary,
    build_ssdi_spearman_summary,
    prepare_ssdi_experimental_data,
)
from upscaling_app.analysis.experimental.ssdi.plotting import (
    save_ssdi_dispersant_comparison_plot,
    save_ssdi_relation_plots,
    save_ssdi_spearman_plot,
)
from upscaling_app.analysis.experimental.ssdi.reporting import (
    print_ssdi_experimental_report,
)


@dataclass
class SSDIExperimentalResult:
    data: pd.DataFrame
    ssdi_only: pd.DataFrame
    dispersant_comparison: pd.DataFrame
    relation_summary: pd.DataFrame
    spearman_summary: pd.DataFrame


def run_ssdi_experimental_analysis() -> SSDIExperimentalResult:
    experiments = load_experiments()

    data = prepare_ssdi_experimental_data(experiments)

    ssdi_only = (
        data.loc[data["dispersion_kind"] == "SSDI"].copy().reset_index(drop=True)
    )

    dispersant_comparison = build_ssdi_dispersant_comparison(
        experiments,
    )

    relation_summary = build_ssdi_relation_summary(
        data,
    )

    spearman_summary = build_ssdi_spearman_summary(
        data,
    )

    return SSDIExperimentalResult(
        data=data,
        ssdi_only=ssdi_only,
        dispersant_comparison=dispersant_comparison,
        relation_summary=relation_summary,
        spearman_summary=spearman_summary,
    )


def run_ssdi_experimental_workflow() -> SSDIExperimentalResult:
    result = run_ssdi_experimental_analysis()

    print_ssdi_experimental_report(result)

    save_ssdi_dispersant_comparison_plot(
        result.dispersant_comparison,
        paths.EXPERIMENTAL_SSDI_FIGURES_DIR / "ssdi_dispersant_comparison.png",
    )

    save_ssdi_spearman_plot(
        result.spearman_summary,
        paths.EXPERIMENTAL_SSDI_FIGURES_DIR / "ssdi_spearman_screening.png",
    )

    save_ssdi_relation_plots(
        result.data,
        result.relation_summary,
        paths.EXPERIMENTAL_SSDI_FIGURES_DIR,
    )

    return result
