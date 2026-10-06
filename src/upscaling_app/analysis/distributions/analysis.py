import numpy as np
import pandas as pd

from upscaling_app.analysis.distributions.metrics import (
    cdf_error_metrics,
    distribution_mass_metrics,
)
from upscaling_app.upscaling.distributions.representation import (
    empirical_cdf,
    experimental_pdf,
)
from upscaling_app.upscaling.distributions.rosin_rammler import (
    rosin_rammler_cdf,
)

from scipy.stats import rankdata, wilcoxon

FIT_METRICS = {
    "cdf": {
        "CDF RMSE": "cdf_rmse",
        "CDF max error": "cdf_max_error",
        "Bin-mass RMSE": "cdf_mass_rmse",
        "Bin-mass max error": "cdf_mass_max_error",
        "Total variation": "cdf_total_variation",
    },
    "moments": {
        "CDF RMSE": "moment_cdf_rmse",
        "CDF max error": "moment_cdf_max_error",
        "Bin-mass RMSE": "moment_mass_rmse",
        "Bin-mass max error": "moment_mass_max_error",
        "Total variation": "moment_total_variation",
    },
}


PAIRED_FIT_METRICS = {
    "cdf_rmse": (
        "cdf_rmse",
        "moment_cdf_rmse",
    ),
    "cdf_max_error": (
        "cdf_max_error",
        "moment_cdf_max_error",
    ),
    "mass_rmse": (
        "cdf_mass_rmse",
        "moment_mass_rmse",
    ),
    "mass_max_error": (
        "cdf_mass_max_error",
        "moment_mass_max_error",
    ),
    "total_variation": (
        "cdf_total_variation",
        "moment_total_variation",
    ),
}


DISTRIBUTION_REGIME_ORDER = [
    "Untreated",
    "SSDI — Corexit",
    "SSDI — Finasol",
    "SSMD",
]


def evaluate_distribution_fits(
    distributions: pd.DataFrame,
    parameters: pd.DataFrame,
) -> pd.DataFrame:
    if parameters["experiment_id"].duplicated().any():
        raise ValueError("parameters contains duplicated experiment_id values.")

    parameter_table = parameters.set_index("experiment_id")

    rows = []

    for (
        experiment_id,
        distribution,
    ) in distributions.groupby(
        "experiment_id",
        sort=False,
    ):
        if experiment_id not in parameter_table.index:
            raise ValueError(
                "Missing fitted parameters for " f"experiment {experiment_id}."
            )

        distribution = distribution.sort_values("droplet_diameter").reset_index(
            drop=True
        )

        diameter = distribution["droplet_diameter"].to_numpy(dtype=float)

        volume_fraction = distribution["volume_fraction"].to_numpy(dtype=float)

        cumulative_fraction = empirical_cdf(volume_fraction)

        pdf_edges, _ = experimental_pdf(
            diameter=diameter,
            volume_fraction=volume_fraction,
        )

        cdf_diameter = pdf_edges[1:]

        fitted = parameter_table.loc[experiment_id]

        # -----------------------------------------------------
        # Method A — direct CDF fit
        # -----------------------------------------------------

        cdf_shape = float(fitted["cdf_shape"])

        cdf_scale = float(fitted["cdf_scale"])

        cdf_prediction = rosin_rammler_cdf(
            diameter=cdf_diameter,
            shape=cdf_shape,
            scale=cdf_scale,
        )

        (
            cdf_rmse,
            cdf_max_error,
        ) = cdf_error_metrics(
            experimental=cumulative_fraction,
            predicted=cdf_prediction,
        )

        cdf_prediction_edges = rosin_rammler_cdf(
            diameter=pdf_edges,
            shape=cdf_shape,
            scale=cdf_scale,
        )

        cdf_bin_fraction = np.diff(cdf_prediction_edges)

        (
            cdf_mass_rmse,
            cdf_mass_max_error,
            cdf_total_variation,
        ) = distribution_mass_metrics(
            experimental=volume_fraction,
            predicted=cdf_bin_fraction,
        )

        # -----------------------------------------------------
        # Method B — discrete moments
        # -----------------------------------------------------

        moment_shape = float(fitted["moment_shape"])

        moment_scale = float(fitted["moment_scale"])

        moment_prediction = rosin_rammler_cdf(
            diameter=cdf_diameter,
            shape=moment_shape,
            scale=moment_scale,
        )

        (
            moment_cdf_rmse,
            moment_cdf_max_error,
        ) = cdf_error_metrics(
            experimental=cumulative_fraction,
            predicted=moment_prediction,
        )

        moment_prediction_edges = rosin_rammler_cdf(
            diameter=pdf_edges,
            shape=moment_shape,
            scale=moment_scale,
        )

        moment_bin_fraction = np.diff(moment_prediction_edges)

        (
            moment_mass_rmse,
            moment_mass_max_error,
            moment_total_variation,
        ) = distribution_mass_metrics(
            experimental=volume_fraction,
            predicted=moment_bin_fraction,
        )

        rows.append(
            {
                "experiment_id": experiment_id,
                "cdf_shape": cdf_shape,
                "cdf_scale": cdf_scale,
                "cdf_rmse": cdf_rmse,
                "cdf_max_error": cdf_max_error,
                "cdf_mass_rmse": cdf_mass_rmse,
                "cdf_mass_max_error": cdf_mass_max_error,
                "cdf_total_variation": cdf_total_variation,
                "moment_shape": moment_shape,
                "moment_scale": moment_scale,
                "moment_cdf_rmse": moment_cdf_rmse,
                "moment_cdf_max_error": moment_cdf_max_error,
                "moment_mass_rmse": moment_mass_rmse,
                "moment_mass_max_error": moment_mass_max_error,
                "moment_total_variation": moment_total_variation,
            }
        )

    return pd.DataFrame(rows)


def summarize_distribution_fit_metrics(
    evaluation: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for method, metrics in FIT_METRICS.items():
        for metric_name, column in metrics.items():
            if column not in evaluation.columns:
                raise ValueError(f"Missing fit metric column: {column}")

            values = evaluation[column].to_numpy(dtype=float)

            values = values[np.isfinite(values)]

            if values.size == 0:
                raise ValueError(f"No finite values available for {column}.")

            rows.append(
                {
                    "method": method,
                    "metric": metric_name,
                    "mean": np.mean(values),
                    "median": np.median(values),
                    "p90": np.quantile(
                        values,
                        0.90,
                    ),
                    "p95": np.quantile(
                        values,
                        0.95,
                    ),
                    "max": np.max(values),
                }
            )

    return pd.DataFrame(rows)


def compare_distribution_fit_methods(
    evaluation: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    comparison = evaluation[
        [
            "experiment_id",
            "oil_id",
            "dispersion_kind",
            "dispersion_tag",
            "nozzle_diameter",
            "has_gas",
        ]
    ].copy()

    summary_rows = []

    for (
        metric,
        (
            cdf_column,
            moment_column,
        ),
    ) in PAIRED_FIT_METRICS.items():
        cdf_values = evaluation[cdf_column].to_numpy(dtype=float)

        moment_values = evaluation[moment_column].to_numpy(dtype=float)

        delta = moment_values - cdf_values

        comparison[f"{metric}_cdf"] = cdf_values

        comparison[f"{metric}_moments"] = moment_values

        comparison[f"{metric}_delta"] = delta

        tie = np.isclose(
            delta,
            0.0,
            rtol=1e-9,
            atol=1e-12,
        )

        cdf_wins = (delta > 0.0) & ~tie

        moment_wins = (delta < 0.0) & ~tie

        winner = np.full(
            len(delta),
            "tie",
            dtype=object,
        )

        winner[cdf_wins] = "cdf"
        winner[moment_wins] = "moments"

        comparison[f"{metric}_winner"] = winner

        n = len(delta)

        summary_rows.append(
            {
                "metric": metric,
                "n": n,
                "cdf_wins": int(np.sum(cdf_wins)),
                "moment_wins": int(np.sum(moment_wins)),
                "ties": int(np.sum(tie)),
                "cdf_win_fraction": (np.sum(cdf_wins) / n),
                "moment_win_fraction": (np.sum(moment_wins) / n),
                "mean_delta": np.mean(delta),
                "median_delta": np.median(delta),
                "p10_delta": np.quantile(
                    delta,
                    0.10,
                ),
                "p90_delta": np.quantile(
                    delta,
                    0.90,
                ),
            }
        )

    summary = pd.DataFrame(summary_rows)

    return (
        comparison,
        summary,
    )


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
                raise ValueError(
                    "Unknown SSDI dispersion tag: " f"{row.dispersion_tag}"
                )

        else:
            raise ValueError("Unknown dispersion kind: " f"{row.dispersion_kind}")

        regimes.append(regime)

    result["distribution_regime"] = regimes

    return result


def summarize_fit_method_comparison_by_regime(
    comparison: pd.DataFrame,
) -> pd.DataFrame:
    data = add_distribution_regime(comparison)

    rows = []

    for regime in DISTRIBUTION_REGIME_ORDER:
        subset = data.loc[data["distribution_regime"] == regime]

        if subset.empty:
            continue

        for metric in PAIRED_FIT_METRICS:
            cdf_column = f"{metric}_cdf"
            moment_column = f"{metric}_moments"
            delta_column = f"{metric}_delta"
            winner_column = f"{metric}_winner"

            cdf_values = subset[cdf_column].to_numpy(dtype=float)
            moment_values = subset[moment_column].to_numpy(dtype=float)
            delta = subset[delta_column].to_numpy(dtype=float)
            winner = subset[winner_column].to_numpy()

            cdf_mean = float(np.mean(cdf_values))
            moment_mean = float(np.mean(moment_values))

            if moment_mean > 0.0:
                mean_improvement_pct = 100.0 * (moment_mean - cdf_mean) / moment_mean
            else:
                mean_improvement_pct = np.nan

            rows.append(
                {
                    "regime": regime,
                    "metric": metric,
                    "n": len(subset),
                    "cdf_mean": cdf_mean,
                    "moment_mean": moment_mean,
                    "cdf_median": float(np.median(cdf_values)),
                    "moment_median": float(np.median(moment_values)),
                    "mean_improvement_pct": (mean_improvement_pct),
                    "cdf_wins": int(np.sum(winner == "cdf")),
                    "moment_wins": int(np.sum(winner == "moments")),
                    "ties": int(np.sum(winner == "tie")),
                    "cdf_win_fraction": float(np.mean(winner == "cdf")),
                    "mean_delta": float(np.mean(delta)),
                    "median_delta": float(np.median(delta)),
                }
            )

    return pd.DataFrame(rows)


def _holm_adjust(
    p_values: np.ndarray,
) -> np.ndarray:
    p_values = np.asarray(
        p_values,
        dtype=float,
    )

    n = len(p_values)

    order = np.argsort(p_values)

    adjusted = np.empty(
        n,
        dtype=float,
    )

    running_max = 0.0

    for rank, index in enumerate(order):
        value = (n - rank) * p_values[index]

        value = min(
            value,
            1.0,
        )

        running_max = max(
            running_max,
            value,
        )

        adjusted[index] = running_max

    return adjusted


def test_distribution_fit_improvement(
    comparison: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for metric in PAIRED_FIT_METRICS:
        delta_column = f"{metric}_delta"

        if delta_column not in comparison.columns:
            raise ValueError(f"Missing comparison column: {delta_column}")

        delta = comparison[delta_column].to_numpy(dtype=float)

        delta = delta[np.isfinite(delta)]

        if delta.size == 0:
            raise ValueError(f"No finite values available for {metric}.")

        nonzero = delta[
            ~np.isclose(
                delta,
                0.0,
                rtol=1e-9,
                atol=1e-12,
            )
        ]

        if nonzero.size == 0:
            statistic = np.nan
            p_value = 1.0
            rank_biserial = 0.0

        else:
            test = wilcoxon(
                nonzero,
                alternative="greater",
                zero_method="wilcox",
                correction=False,
                method="auto",
            )

            statistic = float(test.statistic)

            p_value = float(test.pvalue)

            ranks = rankdata(
                np.abs(nonzero),
                method="average",
            )

            positive_rank_sum = np.sum(ranks[nonzero > 0.0])
            negative_rank_sum = np.sum(ranks[nonzero < 0.0])
            total_rank_sum = positive_rank_sum + negative_rank_sum
            rank_biserial = (positive_rank_sum - negative_rank_sum) / total_rank_sum

        rows.append(
            {
                "metric": metric,
                "n": len(delta),
                "n_nonzero": len(nonzero),
                "median_delta": float(np.median(delta)),
                "mean_delta": float(np.mean(delta)),
                "cdf_win_fraction": float(np.mean(delta > 0.0)),
                "wilcoxon_statistic": (statistic),
                "p_value": (p_value),
                "rank_biserial": float(rank_biserial),
            }
        )

    result = pd.DataFrame(rows)

    result["p_value_holm"] = _holm_adjust(result["p_value"].to_numpy(dtype=float))
    result["significant_0_05"] = result["p_value_holm"] < 0.05

    return result
