import numpy as np
import pandas as pd

from upscaling_app.analysis.distributions.metrics import cdf_error_metrics
from upscaling_app.analysis.distributions.representation import experimental_pdf
from upscaling_app.upscaling.distributions.representation import empirical_cdf
from upscaling_app.upscaling.distributions.rosin_rammler import (
    rosin_rammler_cdf,
    rosin_rammler_pdf,
    rosin_rammler_quantile,
)

FIT_METRICS = {
    "CDF MAE": "cdf_mae",
    "CDF RMSE": "cdf_rmse",
    "CDF max error": "cdf_max_error",
}

DISTRIBUTION_REGIME_ORDER = [
    "Untreated",
    "SSDI — Corexit",
    "SSDI — Finasol",
    "SSMD",
]


def empirical_quantile(
    diameter: np.ndarray,
    cumulative_fraction: np.ndarray,
    quantile: float,
) -> float:
    diameter = np.asarray(diameter, dtype=float)
    cumulative_fraction = np.asarray(cumulative_fraction, dtype=float)

    if diameter.ndim != 1 or cumulative_fraction.ndim != 1:
        raise ValueError("diameter and cumulative_fraction must be one-dimensional.")

    if diameter.size != cumulative_fraction.size:
        raise ValueError("diameter and cumulative_fraction must have the same size.")

    if diameter.size == 0:
        raise ValueError("At least one diameter value is required.")

    if not np.all(np.isfinite(diameter)):
        raise ValueError("diameter contains non-finite values.")

    if not np.all(np.isfinite(cumulative_fraction)):
        raise ValueError("cumulative_fraction contains non-finite values.")

    if np.any(diameter <= 0.0):
        raise ValueError("diameter must be positive.")

    if np.any(np.diff(diameter) <= 0.0):
        raise ValueError("diameter must be strictly increasing.")

    if np.any((cumulative_fraction < 0.0) | (cumulative_fraction > 1.0)):
        raise ValueError("cumulative_fraction must be between 0 and 1.")

    if np.any(np.diff(cumulative_fraction) < 0.0):
        raise ValueError("cumulative_fraction must be non-decreasing.")

    if not 0.0 < quantile < 1.0:
        raise ValueError("quantile must be between 0 and 1.")

    if cumulative_fraction[-1] < quantile:
        raise ValueError("quantile is outside the cumulative distribution range.")

    index = int(np.searchsorted(cumulative_fraction, quantile, side="left"))

    if index == 0:
        return float(diameter[0])

    d0 = diameter[index - 1]
    d1 = diameter[index]
    f0 = cumulative_fraction[index - 1]
    f1 = cumulative_fraction[index]

    if f1 <= f0:
        return float(d1)

    fraction = (quantile - f0) / (f1 - f0)

    return float(d0 + fraction * (d1 - d0))


def _validate_parameter_table(
    parameters: pd.DataFrame,
) -> pd.DataFrame:
    required = {
        "experiment_id",
        "shape",
        "scale",
    }
    missing = required - set(parameters.columns)

    if missing:
        raise ValueError(
            "Missing fitted parameter columns: " + ", ".join(sorted(missing))
        )

    if parameters.empty:
        raise ValueError("No fitted distribution parameters were provided.")

    if parameters["experiment_id"].isna().any():
        raise ValueError("parameters contains missing experiment_id values.")

    if parameters["experiment_id"].duplicated().any():
        raise ValueError("parameters contains duplicated experiment_id values.")

    for column in ("shape", "scale"):
        values = parameters[column].to_numpy(dtype=float)
        invalid = ~np.isfinite(values) | (values <= 0.0)

        if invalid.any():
            raise ValueError(f"parameters contains invalid {column} values.")

    return parameters.set_index("experiment_id")


def evaluate_distribution_fits(
    distributions: pd.DataFrame,
    parameters: pd.DataFrame,
) -> pd.DataFrame:
    required = {
        "experiment_id",
        "droplet_diameter",
        "volume_fraction",
    }
    missing = required - set(distributions.columns)

    if missing:
        raise ValueError("Missing distribution columns: " + ", ".join(sorted(missing)))

    if distributions.empty:
        raise ValueError("No experimental distributions were provided.")

    parameter_table = _validate_parameter_table(parameters)
    rows = []

    for experiment_id, distribution in distributions.groupby(
        "experiment_id",
        sort=False,
    ):
        if experiment_id not in parameter_table.index:
            raise ValueError(
                f"Missing fitted parameters for experiment {experiment_id}."
            )

        distribution = distribution.sort_values("droplet_diameter").reset_index(
            drop=True
        )

        diameter = distribution["droplet_diameter"].to_numpy(dtype=float)
        volume_fraction = distribution["volume_fraction"].to_numpy(dtype=float)
        cumulative_fraction = empirical_cdf(volume_fraction)
        fitted = parameter_table.loc[experiment_id]

        shape = float(fitted["shape"])
        scale = float(fitted["scale"])

        distribution_d50 = empirical_quantile(
            diameter=diameter,
            cumulative_fraction=cumulative_fraction,
            quantile=0.5,
        )

        fitted_d50 = rosin_rammler_quantile(
            quantile=0.5,
            shape=shape,
            scale=scale,
        )

        cdf_prediction = rosin_rammler_cdf(
            diameter=diameter,
            shape=shape,
            scale=scale,
        )

        cdf_mae, cdf_rmse, cdf_max_error = cdf_error_metrics(
            experimental=cumulative_fraction,
            predicted=cdf_prediction,
        )

        rows.append(
            {
                "experiment_id": experiment_id,
                "shape": shape,
                "scale": scale,
                "distribution_d50": distribution_d50,
                "fitted_d50": fitted_d50,
                "cdf_mae": cdf_mae,
                "cdf_rmse": cdf_rmse,
                "cdf_max_error": cdf_max_error,
            }
        )

    return pd.DataFrame(rows)


def build_cdf_validation_points(
    distributions: pd.DataFrame,
    parameters: pd.DataFrame,
) -> pd.DataFrame:
    parameter_table = _validate_parameter_table(parameters)
    frames = []

    for experiment_id, distribution in distributions.groupby(
        "experiment_id",
        sort=False,
    ):
        if experiment_id not in parameter_table.index:
            raise ValueError(
                f"Missing fitted parameters for experiment {experiment_id}."
            )

        data = distribution.sort_values("droplet_diameter").reset_index(drop=True)

        diameter = data["droplet_diameter"].to_numpy(dtype=float)
        volume_fraction = data["volume_fraction"].to_numpy(dtype=float)
        experimental_cdf = empirical_cdf(volume_fraction)
        fitted = parameter_table.loc[experiment_id]

        fitted_cdf = rosin_rammler_cdf(
            diameter=diameter,
            shape=float(fitted["shape"]),
            scale=float(fitted["scale"]),
        )

        frames.append(
            pd.DataFrame(
                {
                    "experiment_id": experiment_id,
                    "droplet_diameter": diameter,
                    "experimental_cdf": experimental_cdf,
                    "fitted_cdf": fitted_cdf,
                    "cdf_residual": fitted_cdf - experimental_cdf,
                }
            )
        )

    if not frames:
        return pd.DataFrame(
            columns=[
                "experiment_id",
                "droplet_diameter",
                "experimental_cdf",
                "fitted_cdf",
                "cdf_residual",
            ]
        )

    return pd.concat(frames, ignore_index=True)


def summarize_distribution_fit_metrics(
    evaluation: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for metric_name, column in FIT_METRICS.items():
        if column not in evaluation.columns:
            raise ValueError(f"Missing fit metric column: {column}")

        values = evaluation[column].to_numpy(dtype=float)
        values = values[np.isfinite(values)]

        if values.size == 0:
            raise ValueError(f"No finite values available for {column}.")

        rows.append(
            {
                "metric": metric_name,
                "mean": float(np.mean(values)),
                "std": float(np.std(values, ddof=1)) if values.size > 1 else 0.0,
                "median": float(np.median(values)),
                "p90": float(np.quantile(values, 0.90)),
                "p95": float(np.quantile(values, 0.95)),
                "max": float(np.max(values)),
            }
        )

    return pd.DataFrame(rows)


def add_distribution_regime(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()
    regimes = []

    for row in result.itertuples(index=False):
        dispersion_kind = str(row.dispersion_kind).strip().lower()
        dispersion_tag = str(row.dispersion_tag).strip().lower()

        if dispersion_kind == "untreated":
            regime = "Untreated"
        elif dispersion_kind == "ssmd":
            regime = "SSMD"
        elif dispersion_kind == "ssdi":
            if "c9500" in dispersion_tag:
                regime = "SSDI — Corexit"
            elif "ibc" in dispersion_tag:
                regime = "SSDI — Finasol"
            else:
                raise ValueError(f"Unknown SSDI dispersion tag: {row.dispersion_tag}")
        else:
            raise ValueError(f"Unknown dispersion kind: {row.dispersion_kind}")

        regimes.append(regime)

    result["distribution_regime"] = regimes

    return result


def summarize_distribution_fit_metrics_by_regime(
    evaluation: pd.DataFrame,
) -> pd.DataFrame:
    data = add_distribution_regime(evaluation)
    rows = []

    for regime in DISTRIBUTION_REGIME_ORDER:
        subset = data.loc[data["distribution_regime"] == regime]

        if subset.empty:
            continue

        for metric_name, column in FIT_METRICS.items():
            values = subset[column].to_numpy(dtype=float)
            values = values[np.isfinite(values)]

            if values.size == 0:
                continue

            rows.append(
                {
                    "regime": regime,
                    "metric": metric_name,
                    "n": int(values.size),
                    "mean": float(np.mean(values)),
                    "std": (float(np.std(values, ddof=1)) if values.size > 1 else 0.0),
                    "median": float(np.median(values)),
                    "p90": float(np.quantile(values, 0.90)),
                    "p95": float(np.quantile(values, 0.95)),
                    "max": float(np.max(values)),
                }
            )

    return pd.DataFrame(rows)


def build_distribution_fit_curves(
    distribution: pd.DataFrame,
    fitted: pd.Series,
) -> dict[str, np.ndarray | float]:
    distribution = distribution.sort_values("droplet_diameter").reset_index(drop=True)

    diameter = distribution["droplet_diameter"].to_numpy(dtype=float)
    volume_fraction = distribution["volume_fraction"].to_numpy(dtype=float)
    cumulative_fraction = empirical_cdf(volume_fraction)

    pdf_edges, experimental_density = experimental_pdf(
        diameter=diameter,
        volume_fraction=volume_fraction,
    )

    shape = float(fitted["shape"])
    scale = float(fitted["scale"])

    fitted_cdf_at_data = rosin_rammler_cdf(
        diameter=diameter,
        shape=shape,
        scale=scale,
    )

    experimental_d999 = empirical_quantile(
        diameter=diameter,
        cumulative_fraction=cumulative_fraction,
        quantile=0.999,
    )

    fitted_d999 = rosin_rammler_quantile(
        quantile=0.999,
        shape=shape,
        scale=scale,
    )

    plot_max_diameter = 1.15 * max(
        experimental_d999,
        float(fitted_d999),
    )

    rr_min = max(
        float(pdf_edges[0]),
        np.finfo(float).tiny,
    )

    rr_diameter = np.geomspace(
        rr_min,
        plot_max_diameter,
        500,
    )

    fitted_cdf = rosin_rammler_cdf(
        diameter=rr_diameter,
        shape=shape,
        scale=scale,
    )

    fitted_pdf = rosin_rammler_pdf(
        diameter=rr_diameter,
        shape=shape,
        scale=scale,
    )

    return {
        "diameter": diameter,
        "experimental_cdf": cumulative_fraction,
        "fitted_cdf_at_data": fitted_cdf_at_data,
        "pdf_edges": pdf_edges,
        "experimental_pdf": experimental_density,
        "rr_diameter": rr_diameter,
        "fitted_cdf": fitted_cdf,
        "fitted_pdf": fitted_pdf,
        "plot_max_diameter": plot_max_diameter,
    }


def add_d50_diagnostics(
    evaluation: pd.DataFrame,
) -> pd.DataFrame:
    required = {
        "measured_d50",
        "distribution_d50",
        "fitted_d50",
    }
    missing = required - set(evaluation.columns)

    if missing:
        raise ValueError(
            "Missing D50 diagnostic columns: " + ", ".join(sorted(missing))
        )

    result = evaluation.copy()

    for column in required:
        values = result[column].to_numpy(dtype=float)

        if not np.all(np.isfinite(values)) or np.any(values <= 0.0):
            raise ValueError(f"{column} must contain finite positive values.")

    fit_error = result["fitted_d50"] - result["distribution_d50"]
    fit_relative_error = fit_error / result["distribution_d50"]

    result["fit_d50_error"] = fit_error
    result["fit_d50_abs_error"] = np.abs(fit_error)
    result["fit_d50_relative_error"] = fit_relative_error
    result["fit_d50_abs_relative_error"] = np.abs(fit_relative_error)

    source_error = result["distribution_d50"] - result["measured_d50"]
    source_relative_error = source_error / result["measured_d50"]

    result["source_d50_error"] = source_error
    result["source_d50_abs_error"] = np.abs(source_error)
    result["source_d50_relative_error"] = source_relative_error
    result["source_d50_abs_relative_error"] = np.abs(source_relative_error)

    return result


def _summarize_d50_pair(
    reference: np.ndarray,
    estimate: np.ndarray,
    *,
    comparison: str,
    reference_name: str,
    estimate_name: str,
) -> dict[str, float | int | str]:
    reference = np.asarray(reference, dtype=float)
    estimate = np.asarray(estimate, dtype=float)

    if reference.size != estimate.size:
        raise ValueError("D50 reference and estimate must have the same size.")

    if reference.size == 0:
        raise ValueError("No D50 values are available for comparison.")

    if (
        not np.all(np.isfinite(reference))
        or not np.all(np.isfinite(estimate))
        or np.any(reference <= 0.0)
        or np.any(estimate <= 0.0)
    ):
        raise ValueError("D50 comparisons require finite positive values.")

    error = estimate - reference
    relative_error = error / reference
    absolute_relative_error = np.abs(relative_error)

    reference_mean = np.mean(reference)
    total_sum_squares = np.sum((reference - reference_mean) ** 2)
    residual_sum_squares = np.sum(error**2)

    log_reference = np.log(reference)
    log_estimate = np.log(estimate)
    log_error = log_estimate - log_reference
    log_total_sum_squares = np.sum((log_reference - np.mean(log_reference)) ** 2)

    return {
        "comparison": comparison,
        "reference": reference_name,
        "estimate": estimate_name,
        "n": int(reference.size),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "mae": float(np.mean(np.abs(error))),
        "bias": float(np.mean(error)),
        "std_error": float(np.std(error, ddof=1)) if error.size > 1 else 0.0,
        "mape_pct": float(100.0 * np.mean(absolute_relative_error)),
        "median_abs_relative_error_pct": float(
            100.0 * np.median(absolute_relative_error)
        ),
        "p95_abs_relative_error_pct": float(
            100.0 * np.quantile(absolute_relative_error, 0.95)
        ),
        "max_abs_relative_error_pct": float(100.0 * np.max(absolute_relative_error)),
        "r2": (
            float(1.0 - residual_sum_squares / total_sum_squares)
            if total_sum_squares > 0.0
            else np.nan
        ),
        "log_mse": float(np.mean(log_error**2)),
        "r2_log": (
            float(1.0 - np.sum(log_error**2) / log_total_sum_squares)
            if log_total_sum_squares > 0.0
            else np.nan
        ),
    }


def summarize_d50_diagnostics(
    evaluation: pd.DataFrame,
) -> pd.DataFrame:
    required = {
        "distribution_d50",
        "fitted_d50",
        "measured_d50",
    }
    missing = required - set(evaluation.columns)

    if missing:
        raise ValueError("Missing D50 summary columns: " + ", ".join(sorted(missing)))

    distribution_d50 = evaluation["distribution_d50"].to_numpy(dtype=float)

    rows = [
        _summarize_d50_pair(
            reference=distribution_d50,
            estimate=evaluation["fitted_d50"].to_numpy(dtype=float),
            comparison="fit_vs_distribution",
            reference_name="distribution_d50",
            estimate_name="fitted_d50",
        ),
        _summarize_d50_pair(
            reference=evaluation["measured_d50"].to_numpy(dtype=float),
            estimate=distribution_d50,
            comparison="distribution_vs_reported",
            reference_name="measured_d50",
            estimate_name="distribution_d50",
        ),
    ]

    return pd.DataFrame(rows)


def select_representative_fit_cases(
    evaluation: pd.DataFrame,
    metric: str = "cdf_rmse",
    n_each: int = 3,
) -> pd.DataFrame:
    if metric not in evaluation.columns:
        raise ValueError(f"Unknown ranking metric: {metric}")

    if len(evaluation) < 3 * n_each:
        raise ValueError("Not enough experiments to select representative fit cases.")

    ranked = evaluation.sort_values(metric).reset_index(drop=True)

    best = ranked.head(n_each).copy()
    best["case_group"] = "best"
    best["case_rank"] = np.arange(1, len(best) + 1)

    middle_start = len(ranked) // 2 - n_each // 2
    middle = ranked.iloc[middle_start : middle_start + n_each].copy()
    middle["case_group"] = "middle"
    middle["case_rank"] = np.arange(1, len(middle) + 1)

    worst = ranked.tail(n_each).copy()
    worst = worst.sort_values(metric, ascending=False).reset_index(drop=True)
    worst["case_group"] = "worst"
    worst["case_rank"] = np.arange(1, len(worst) + 1)

    return pd.concat(
        [
            best,
            middle,
            worst,
        ],
        ignore_index=True,
    )
