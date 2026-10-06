import numpy as np
import pandas as pd


def normalize_distribution(
    fraction: np.ndarray,
) -> np.ndarray:
    fraction = np.asarray(
        fraction,
        dtype=float,
    )

    if not np.all(np.isfinite(fraction)):
        raise ValueError("Distribution contains non-finite fractions.")

    if np.any(fraction < 0.0):
        raise ValueError("Distribution contains negative fractions.")

    total = fraction.sum()

    if total <= 0.0:
        raise ValueError("Distribution has zero total volume fraction.")

    return fraction / total


def empirical_quantile(
    diameter: np.ndarray,
    fraction: np.ndarray,
    quantile: float,
) -> float:
    diameter = np.asarray(
        diameter,
        dtype=float,
    )

    fraction = np.asarray(
        fraction,
        dtype=float,
    )

    if diameter.size != fraction.size:
        raise ValueError("diameter and fraction must have the same size.")

    if not 0.0 <= quantile <= 1.0:
        raise ValueError("quantile must be between 0 and 1.")

    order = np.argsort(diameter)

    diameter = diameter[order]
    fraction = fraction[order]

    weights = normalize_distribution(fraction)

    cumulative = np.cumsum(weights)

    upper_index = np.searchsorted(
        cumulative,
        quantile,
        side="left",
    )

    if upper_index == 0:
        return float(diameter[0])

    if upper_index >= diameter.size:
        return float(diameter[-1])

    lower_index = upper_index - 1

    d0 = diameter[lower_index]

    d1 = diameter[upper_index]

    f0 = cumulative[lower_index]

    f1 = cumulative[upper_index]

    if np.isclose(
        f1,
        f0,
    ):
        return float(d1)

    alpha = (quantile - f0) / (f1 - f0)

    return float(d0 + alpha * (d1 - d0))


def discrete_moments(
    diameter: np.ndarray,
    fraction: np.ndarray,
) -> tuple[
    float,
    float,
    float,
]:
    diameter = np.asarray(
        diameter,
        dtype=float,
    )

    fraction = np.asarray(
        fraction,
        dtype=float,
    )

    if diameter.size != fraction.size:
        raise ValueError("diameter and fraction must have the same size.")

    weights = normalize_distribution(fraction)

    mean = np.sum(weights * diameter)

    variance = np.sum(weights * (diameter - mean) ** 2)

    std = np.sqrt(variance)

    return (
        float(mean),
        float(variance),
        float(std),
    )


def summarize_distribution(
    distribution: pd.DataFrame,
) -> pd.Series:
    distribution = distribution.sort_values("droplet_diameter")

    diameter = distribution["droplet_diameter"].to_numpy(dtype=float)
    fraction = distribution["volume_fraction"].to_numpy(dtype=float)

    total_fraction = fraction.sum()

    mean, _, std = discrete_moments(
        diameter=diameter,
        fraction=fraction,
    )

    d10 = empirical_quantile(
        diameter=diameter,
        fraction=fraction,
        quantile=0.10,
    )

    d50 = empirical_quantile(
        diameter=diameter,
        fraction=fraction,
        quantile=0.50,
    )

    d90 = empirical_quantile(
        diameter=diameter,
        fraction=fraction,
        quantile=0.90,
    )

    d_peak = float(diameter[np.argmax(fraction)])

    span = (d90 - d10) / d50

    return pd.Series(
        {
            "d10": d10,
            "d50": d50,
            "d90": d90,
            "d_peak": d_peak,
            "mean_diameter": mean,
            "std_diameter": std,
            "span": span,
            "volume_fraction_sum": total_fraction,
        }
    )


def summarize_distributions(
    distributions: pd.DataFrame,
) -> pd.DataFrame:
    summaries = []

    for (
        experiment_id,
        distribution,
    ) in distributions.groupby(
        "experiment_id",
        sort=False,
    ):
        summary = summarize_distribution(distribution)

        summary["experiment_id"] = experiment_id

        summaries.append(summary)

    result = pd.DataFrame(summaries)

    columns = [
        "experiment_id",
        "d10",
        "d50",
        "d90",
        "d_peak",
        "mean_diameter",
        "std_diameter",
        "span",
        "volume_fraction_sum",
    ]

    return result[columns]


def cumulative_at_diameter(
    diameter: np.ndarray,
    fraction: np.ndarray,
    target_diameter: float,
) -> float:
    diameter = np.asarray(
        diameter,
        dtype=float,
    )

    fraction = np.asarray(
        fraction,
        dtype=float,
    )

    if diameter.size != fraction.size:
        raise ValueError("diameter and fraction must have the same size.")

    order = np.argsort(diameter)

    diameter = diameter[order]

    fraction = fraction[order]

    weights = normalize_distribution(fraction)

    cumulative = np.cumsum(weights)

    return float(
        np.interp(
            target_diameter,
            diameter,
            cumulative,
            left=0.0,
            right=1.0,
        )
    )


def compare_distribution_d50(
    summary: pd.DataFrame,
    experiments: pd.DataFrame,
) -> pd.DataFrame:
    comparison = summary[
        [
            "experiment_id",
            "d50",
            "d_peak",
        ]
    ].merge(
        experiments[
            [
                "experiment_id",
                "oil_id",
                "dispersion_kind",
                "dispersion_tag",
                "nozzle_diameter",
                "has_gas",
                "measured_d50",
                "source_sheet",
            ]
        ],
        on="experiment_id",
        how="left",
        validate="one_to_one",
    )

    if comparison["measured_d50"].isna().any():
        raise ValueError("Missing experiment metadata for one or more distributions.")

    comparison["d50_error"] = comparison["d50"] - comparison["measured_d50"]

    comparison["d50_relative_error"] = (
        comparison["d50_error"] / comparison["measured_d50"]
    )

    comparison["d_peak_relative_error"] = (
        comparison["d_peak"] - comparison["measured_d50"]
    ) / comparison["measured_d50"]

    return comparison


def add_reported_d50_percentile(
    comparison: pd.DataFrame,
    distributions: pd.DataFrame,
) -> pd.DataFrame:
    target_d50 = comparison.set_index("experiment_id")["measured_d50"]

    diagnostics = []

    for (
        experiment_id,
        distribution,
    ) in distributions.groupby(
        "experiment_id",
        sort=False,
    ):
        if experiment_id not in target_d50.index:
            raise ValueError("Missing experiment metadata for " f"{experiment_id}.")

        diameter = distribution["droplet_diameter"].to_numpy(dtype=float)

        fraction = distribution["volume_fraction"].to_numpy(dtype=float)

        measured_d50 = float(target_d50.loc[experiment_id])

        cdf_at_measured_d50 = cumulative_at_diameter(
            diameter=diameter,
            fraction=fraction,
            target_diameter=measured_d50,
        )

        diagnostics.append(
            {
                "experiment_id": experiment_id,
                "cdf_at_measured_d50": (cdf_at_measured_d50),
                "reported_percentile": (100.0 * cdf_at_measured_d50),
                "percentile_error": (cdf_at_measured_d50 - 0.5),
            }
        )

    diagnostics = pd.DataFrame(diagnostics)

    return comparison.merge(
        diagnostics,
        on="experiment_id",
        how="left",
        validate="one_to_one",
    )


def analyze_distribution_consistency(
    distributions: pd.DataFrame,
    experiments: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    summary = summarize_distributions(distributions)

    comparison = compare_distribution_d50(
        summary=summary,
        experiments=experiments,
    )

    comparison = add_reported_d50_percentile(
        comparison=comparison,
        distributions=distributions,
    )

    return (
        summary,
        comparison,
    )
