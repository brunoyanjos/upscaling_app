from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.experimental.data import (
    filter_by_dispersion,
    load_experiments,
)
from upscaling_app.analysis.experimental.summary.analysis import (
    summarize_completeness,
    summarize_dataset,
    summarize_oil_coverage,
    summarize_oil_treatment_coverage,
    summarize_regimes,
)
from upscaling_app.analysis.experimental.summary.plotting import (
    save_oil_treatment_coverage_plot,
    save_regime_coverage_plot,
)
from upscaling_app.analysis.experimental.summary.reporting import (
    print_experimental_summary_report,
)

DISPERSION_KINDS: Final[dict[str, str | None]] = {
    "all": None,
    "untreated": "Untreated",
    "ssdi": "SSDI",
    "ssmd": "SSMD",
}


@dataclass
class ExperimentalSummaryResult:
    data: pd.DataFrame
    dataset_summary: dict[str, int]
    regime_summary: pd.DataFrame
    oil_coverage: pd.DataFrame
    oil_treatment_coverage: pd.DataFrame
    completeness: pd.DataFrame


def run_experimental_summary(
    kind: str = "all",
) -> ExperimentalSummaryResult:
    if kind not in DISPERSION_KINDS:
        available = ", ".join(DISPERSION_KINDS)

        raise ValueError(
            f"Unknown dispersion kind {kind!r}. " f"Available kinds: {available}."
        )

    data = load_experiments()

    data = filter_by_dispersion(
        data,
        dispersion_kind=DISPERSION_KINDS[kind],
    )

    return ExperimentalSummaryResult(
        data=data,
        dataset_summary=summarize_dataset(data),
        regime_summary=summarize_regimes(data),
        oil_coverage=summarize_oil_coverage(data),
        oil_treatment_coverage=summarize_oil_treatment_coverage(data),
        completeness=summarize_completeness(data),
    )


def run_experimental_summary_workflow(
    kind: str = "all",
) -> ExperimentalSummaryResult:
    result = run_experimental_summary(kind=kind)

    print_experimental_summary_report(result)

    save_regime_coverage_plot(
        result.regime_summary,
        paths.EXPERIMENTAL_SUMMARY_FIGURES_DIR / "experimental_regime_coverage.png",
    )

    save_oil_treatment_coverage_plot(
        result.oil_treatment_coverage,
        paths.EXPERIMENTAL_SUMMARY_FIGURES_DIR / "experimental_oil_coverage.png",
    )

    return result
