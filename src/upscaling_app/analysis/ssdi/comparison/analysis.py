from dataclasses import dataclass

import pandas as pd

from upscaling_app.analysis.ssdi.io.data import (
    load_ssdi_results,
)
from upscaling_app.analysis.ssdi.metrics import (
    calculate_global_metrics,
)
from upscaling_app.analysis.ssdi.performance.analysis import (
    prepare_performance_results,
)
from upscaling_app.upscaling.ssdi.versions import (
    BASELINE_VERSION,
    FILTERED_VERSION,
    OIL_EXTENDED_SENSITIVITY_VERSION,
    OIL_RESIDUAL_SENSITIVITY_VERSION,
    OIL_WISE_VERSION,
    REFERENCE_VERSION,
)


@dataclass(frozen=True)
class ComparisonModel:
    model_version: str
    label: str
    analysis_type: str
    population: str


COMPARISON_MODELS = (
    ComparisonModel(
        model_version=REFERENCE_VERSION,
        label="SINTEF reference",
        analysis_type="reference",
        population="complete",
    ),
    ComparisonModel(
        model_version=BASELINE_VERSION,
        label="Global baseline",
        analysis_type="global_calibration",
        population="complete",
    ),
    ComparisonModel(
        model_version=FILTERED_VERSION,
        label="IQR sensitivity",
        analysis_type="sensitivity",
        population="IQR-retained",
    ),
    ComparisonModel(
        model_version=OIL_RESIDUAL_SENSITIVITY_VERSION,
        label="Oil residual",
        analysis_type="sensitivity",
        population="exclude 3016, 4665",
    ),
    ComparisonModel(
        model_version=OIL_EXTENDED_SENSITIVITY_VERSION,
        label="Oil extended",
        analysis_type="sensitivity",
        population="exclude 3016, 4662, 4665",
    ),
    ComparisonModel(
        model_version=OIL_WISE_VERSION,
        label="Oil-wise",
        analysis_type="oil_specific_calibration",
        population="complete",
    ),
)


def build_ssdi_model_comparison() -> pd.DataFrame:
    rows = []

    for model in COMPARISON_MODELS:
        predictions = load_ssdi_results(
            model.model_version,
        )

        results = prepare_performance_results(
            predictions,
        )

        metrics = calculate_global_metrics(
            results,
        )

        rows.append(
            {
                "model_version": model.model_version,
                "model": model.label,
                "analysis_type": model.analysis_type,
                "population": model.population,
                "n": len(results),
                "log_mse": metrics["log_mse"],
                "r2": metrics["r2"],
                "rmse": metrics["rmse"],
                "mape": metrics["mape"],
                "mean_log_residual": float(results["log_residual"].mean()),
                "std_log_residual": float(results["log_residual"].std()),
            }
        )

    return pd.DataFrame(rows)
