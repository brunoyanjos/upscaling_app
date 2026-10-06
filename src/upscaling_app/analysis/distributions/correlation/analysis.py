from __future__ import annotations

import numpy as np
import pandas as pd

from scipy.stats import (
    pearsonr,
    spearmanr,
)

SSMD_PHYSICAL_MODEL_SPECS = {
    "M0 — intercept": [],
    "M1 — regime physics": [
        "log_untreated_froude",
        "untreated_gas_void_fraction",
    ],
    "M2 — oil properties": [
        "log_oil_viscosity",
        "log_untreated_ift",
        "log_oil_density",
    ],
    "M3 — regime + oil": [
        "log_untreated_froude",
        "untreated_gas_void_fraction",
        "log_oil_viscosity",
        "log_untreated_ift",
        "log_oil_density",
    ],
    "M4 — M3 + momentum": [
        "log_untreated_froude",
        "untreated_gas_void_fraction",
        "log_oil_viscosity",
        "log_untreated_ift",
        "log_oil_density",
        "log_momentum_amplification",
    ],
    "M5 — M3 + power": [
        "log_untreated_froude",
        "untreated_gas_void_fraction",
        "log_oil_viscosity",
        "log_untreated_ift",
        "log_oil_density",
        "log_kinetic_power_ratio",
    ],
}

COMMON_FEATURES = [
    "nozzle_diameter",
    "oil_viscosity",
    "ift",
    "oil_density",
    "void_fraction",
    "mixed_density",
    "volumetric_velocity",
    "modified_velocity",
    "reduced_gravity",
    "froude",
    "effective_velocity",
    "reynolds",
    "weber",
    "capillary",
]


SSMD_FEATURES = [
    "water_jet_fraction",
    "water_flow",
    "water_nozzle_diameter",
    "untreated_ift",
    "untreated_gas_void_fraction",
    "untreated_mixed_density",
    "untreated_volumetric_velocity",
    "untreated_modified_velocity",
    "untreated_reduced_gravity",
    "untreated_froude",
    "untreated_effective_velocity",
    "water_velocity",
    "water_momentum_flux",
    "water_kinetic_power",
    "oil_momentum_flux",
    "momentum_amplification",
    "oil_kinetic_power",
    "kinetic_power_ratio",
]

UNTREATED_CANDIDATE_FEATURES = [
    "froude",
    "reynolds",
    "weber",
    "capillary",
    "oil_viscosity",
    "ift",
    "oil_density",
    "void_fraction",
    "nozzle_diameter",
]


SSDI_CANDIDATE_FEATURES = [
    "froude",
    "reynolds",
    "weber",
    "capillary",
    "oil_viscosity",
    "ift",
    "oil_density",
    "void_fraction",
    "nozzle_diameter",
]


SSMD_CANDIDATE_FEATURES = [
    "untreated_froude",
    "momentum_amplification",
    "kinetic_power_ratio",
    "water_momentum_flux",
    "water_kinetic_power",
    "water_jet_fraction",
    "oil_viscosity",
    "untreated_ift",
    "oil_density",
    "void_fraction",
    "nozzle_diameter",
]

SSMD_WITHIN_GROUP_KEYS = [
    "oil_id",
    "nozzle_diameter",
    "has_gas",
]


SSMD_WITHIN_FEATURES = [
    "water_jet_fraction",
    "momentum_amplification",
    "kinetic_power_ratio",
    "water_momentum_flux",
    "water_kinetic_power",
]


SSMD_M4_PREDICTORS = [
    "log_untreated_froude",
    "untreated_gas_void_fraction",
    "log_oil_viscosity",
    "log_untreated_ift",
    "log_oil_density",
    "log_momentum_amplification",
]


def _screen_feature(
    data: pd.DataFrame,
    feature: str,
) -> dict[str, object]:
    subset = data[
        [
            "shape",
            feature,
        ]
    ].dropna()

    if subset.empty:
        return {
            "feature": feature,
            "n": 0,
            "n_unique": 0,
            "spearman_rho": np.nan,
            "p_value": np.nan,
        }

    n_unique = subset[feature].nunique()

    if n_unique < 2:
        rho = np.nan
        p_value = np.nan
    else:
        rho, p_value = spearmanr(
            subset[feature],
            subset["shape"],
        )

    return {
        "feature": feature,
        "n": len(subset),
        "n_unique": n_unique,
        "spearman_rho": rho,
        "p_value": p_value,
    }


def _screen_population(
    data: pd.DataFrame,
    *,
    population: str,
    features: list[str],
) -> pd.DataFrame:
    rows = []

    for feature in features:
        row = _screen_feature(
            data=data,
            feature=feature,
        )

        row["population"] = population

        rows.append(row)

    result = pd.DataFrame(rows)

    result["abs_spearman_rho"] = result["spearman_rho"].abs()

    return (
        result[
            [
                "population",
                "feature",
                "n",
                "n_unique",
                "spearman_rho",
                "abs_spearman_rho",
                "p_value",
            ]
        ]
        .sort_values(
            [
                "population",
                "abs_spearman_rho",
            ],
            ascending=[
                True,
                False,
            ],
        )
        .reset_index(drop=True)
    )


def _screen_predictor_redundancy(
    data: pd.DataFrame,
    *,
    population: str,
    features: list[str],
) -> pd.DataFrame:
    rows = []

    for i, feature_a in enumerate(features):
        for feature_b in features[i + 1 :]:
            subset = data[
                [
                    feature_a,
                    feature_b,
                ]
            ].dropna()

            if subset.empty:
                continue

            if subset[feature_a].nunique() < 2 or subset[feature_b].nunique() < 2:
                continue

            rho, _ = spearmanr(
                subset[feature_a],
                subset[feature_b],
            )

            rows.append(
                {
                    "population": population,
                    "feature_a": feature_a,
                    "feature_b": feature_b,
                    "n": len(subset),
                    "spearman_rho": rho,
                    "abs_spearman_rho": abs(rho),
                }
            )

    return pd.DataFrame(rows)


def screen_predictor_redundancy(
    data: pd.DataFrame,
) -> pd.DataFrame:
    untreated = data.loc[data["dispersion_kind"].eq("Untreated")]

    ssdi = data.loc[data["dispersion_kind"].eq("SSDI")]

    ssmd = data.loc[data["dispersion_kind"].eq("SSMD")]

    results = [
        _screen_predictor_redundancy(
            untreated,
            population="Untreated",
            features=UNTREATED_CANDIDATE_FEATURES,
        ),
        _screen_predictor_redundancy(
            ssdi,
            population="SSDI",
            features=SSDI_CANDIDATE_FEATURES,
        ),
        _screen_predictor_redundancy(
            ssmd,
            population="SSMD",
            features=SSMD_CANDIDATE_FEATURES,
        ),
    ]

    result = pd.concat(
        results,
        ignore_index=True,
    )

    return result.sort_values(
        [
            "population",
            "abs_spearman_rho",
        ],
        ascending=[
            True,
            False,
        ],
    ).reset_index(drop=True)


def screen_shape_correlations(
    data: pd.DataFrame,
) -> pd.DataFrame:
    untreated = data.loc[data["dispersion_kind"].eq("Untreated")]

    ssdi = data.loc[data["dispersion_kind"].eq("SSDI")]

    ssmd = data.loc[data["dispersion_kind"].eq("SSMD")]

    untreated_screening = _screen_population(
        untreated,
        population="Untreated",
        features=COMMON_FEATURES,
    )

    ssdi_screening = _screen_population(
        ssdi,
        population="SSDI",
        features=COMMON_FEATURES,
    )

    ssmd_screening = _screen_population(
        ssmd,
        population="SSMD",
        features=[
            *COMMON_FEATURES,
            *SSMD_FEATURES,
        ],
    )

    return pd.concat(
        [
            untreated_screening,
            ssdi_screening,
            ssmd_screening,
        ],
        ignore_index=True,
    )


def prepare_ssmd_within_group_data(
    data: pd.DataFrame,
) -> pd.DataFrame:
    ssmd = data.loc[data["dispersion_kind"].eq("SSMD")].copy()

    required_columns = [
        "experiment_id",
        *SSMD_WITHIN_GROUP_KEYS,
        "shape",
        *SSMD_WITHIN_FEATURES,
    ]

    missing = [column for column in required_columns if column not in ssmd.columns]

    if missing:
        raise ValueError(
            "Missing columns for SSMD within-group " f"analysis: {missing}"
        )

    group_sizes = ssmd.groupby(SSMD_WITHIN_GROUP_KEYS).size()

    invalid_groups = group_sizes.loc[group_sizes != 3]

    if not invalid_groups.empty:
        raise ValueError(
            "Expected exactly three SSMD treatment "
            "intensities per oil/nozzle/gas group:\n"
            f"{invalid_groups.to_string()}"
        )

    positive_columns = [
        "shape",
        *SSMD_WITHIN_FEATURES,
    ]

    for column in positive_columns:
        values = ssmd[column].to_numpy(dtype=float)

        invalid = ~np.isfinite(values) | (values <= 0.0)

        if invalid.any():
            raise ValueError(
                f"Invalid values found in {column!r} " "for SSMD within-group analysis."
            )

        log_column = f"log_{column}"

        delta_column = f"delta_log_{column}"

        ssmd[log_column] = np.log(ssmd[column])

        ssmd[delta_column] = ssmd[log_column] - ssmd.groupby(SSMD_WITHIN_GROUP_KEYS)[
            log_column
        ].transform("mean")

    return ssmd.sort_values(
        [
            *SSMD_WITHIN_GROUP_KEYS,
            "water_jet_fraction",
        ]
    ).reset_index(drop=True)


def screen_ssmd_within_group_relations(
    data: pd.DataFrame,
) -> pd.DataFrame:
    centered = prepare_ssmd_within_group_data(data)

    y = centered["delta_log_shape"].to_numpy(dtype=float)

    rows = []

    for feature in SSMD_WITHIN_FEATURES:
        x = centered[f"delta_log_{feature}"].to_numpy(dtype=float)

        if np.allclose(
            x,
            0.0,
        ):
            continue

        slope = np.sum(x * y) / np.sum(x**2)

        prediction = slope * x

        residual = y - prediction

        ss_res = np.sum(residual**2)

        ss_tot = np.sum(y**2)

        r_squared = 1.0 - ss_res / ss_tot

        pearson_r, _ = pearsonr(
            x,
            y,
        )

        spearman_rho, _ = spearmanr(
            x,
            y,
        )

        rows.append(
            {
                "feature": feature,
                "n": len(centered),
                "n_groups": centered.groupby(SSMD_WITHIN_GROUP_KEYS).ngroups,
                "slope": slope,
                "r_squared": r_squared,
                "pearson_r": pearson_r,
                "spearman_rho": spearman_rho,
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values(
            "r_squared",
            ascending=False,
        )
        .reset_index(drop=True)
    )


def _linear_r_squared(
    y: np.ndarray,
    design: pd.DataFrame,
) -> float:
    x = design.to_numpy(
        dtype=float,
    )

    x = np.column_stack(
        [
            np.ones(len(x)),
            x,
        ]
    )

    coefficients, *_ = np.linalg.lstsq(
        x,
        y,
        rcond=None,
    )

    prediction = x @ coefficients

    ss_res = np.sum((y - prediction) ** 2)

    ss_tot = np.sum((y - np.mean(y)) ** 2)

    return 1.0 - ss_res / ss_tot


def _ssmd_regime_labels(
    data: pd.DataFrame,
) -> pd.Series:
    nozzle = data["nozzle_diameter"].to_numpy(dtype=float)

    gas = data["has_gas"].to_numpy(dtype=bool)

    labels = np.select(
        [
            np.isclose(
                nozzle,
                0.002,
            )
            & ~gas,
            np.isclose(
                nozzle,
                0.003,
            )
            & ~gas,
            np.isclose(
                nozzle,
                0.002,
            )
            & gas,
        ],
        [
            "2 mm — no gas",
            "3 mm — no gas",
            "2 mm — gas",
        ],
        default="unknown",
    )

    result = pd.Series(
        labels,
        index=data.index,
        dtype="object",
    )

    if result.eq("unknown").any():
        invalid = data.loc[
            result.eq("unknown"),
            [
                "experiment_id",
                "nozzle_diameter",
                "has_gas",
            ],
        ]

        raise ValueError(
            "Unknown SSMD experimental regime:\n" f"{invalid.to_string(index=False)}"
        )

    return result


def decompose_ssmd_shape_variance(
    data: pd.DataFrame,
) -> pd.DataFrame:
    ssmd = prepare_ssmd_within_group_data(data)

    ssmd["experimental_regime"] = _ssmd_regime_labels(ssmd)

    y = ssmd["log_shape"].to_numpy(dtype=float)

    # ---------------------------------------------------------
    # Categorical diagnostic designs
    # ---------------------------------------------------------

    oil_design = pd.get_dummies(
        ssmd["oil_id"].astype(str),
        prefix="oil",
        drop_first=True,
        dtype=float,
    )

    regime_design = pd.get_dummies(
        ssmd["experimental_regime"],
        prefix="regime",
        drop_first=True,
        dtype=float,
    )

    oil_regime_additive = pd.concat(
        [
            oil_design,
            regime_design,
        ],
        axis=1,
    )

    oil_regime_key = ssmd["oil_id"].astype(str) + " | " + ssmd["experimental_regime"]

    oil_regime_interaction = pd.get_dummies(
        oil_regime_key,
        prefix="oil_regime",
        drop_first=True,
        dtype=float,
    )

    r2_oil = _linear_r_squared(
        y,
        oil_design,
    )

    r2_regime = _linear_r_squared(
        y,
        regime_design,
    )

    r2_oil_regime = _linear_r_squared(
        y,
        oil_regime_additive,
    )

    r2_oil_regime_interaction = _linear_r_squared(
        y,
        oil_regime_interaction,
    )

    rows = [
        {
            "model": "oil",
            "r_squared": r2_oil,
            "delta_r_squared": r2_oil,
        },
        {
            "model": "regime",
            "r_squared": r2_regime,
            "delta_r_squared": r2_regime,
        },
        {
            "model": "oil + regime",
            "r_squared": r2_oil_regime,
            "delta_r_squared": (
                r2_oil_regime
                - max(
                    r2_oil,
                    r2_regime,
                )
            ),
        },
        {
            "model": "oil × regime",
            "r_squared": (r2_oil_regime_interaction),
            "delta_r_squared": (r2_oil_regime_interaction - r2_oil_regime),
        },
    ]

    # ---------------------------------------------------------
    # Add within-condition treatment variation.
    #
    # These centered features contain only variation within:
    #
    # oil_id + nozzle_diameter + has_gas
    # ---------------------------------------------------------

    for feature in [
        "momentum_amplification",
        "kinetic_power_ratio",
        "water_jet_fraction",
    ]:
        design = oil_regime_interaction.copy()

        design[f"within_{feature}"] = ssmd[f"delta_log_{feature}"].to_numpy(dtype=float)

        r_squared = _linear_r_squared(
            y,
            design,
        )

        rows.append(
            {
                "model": ("oil × regime" f" + within {feature}"),
                "r_squared": r_squared,
                "delta_r_squared": (r_squared - r2_oil_regime_interaction),
            }
        )

    return pd.DataFrame(rows).reset_index(drop=True)


def prepare_ssmd_physical_model_data(
    data: pd.DataFrame,
) -> pd.DataFrame:
    ssmd = data.loc[data["dispersion_kind"].eq("SSMD")].copy()

    positive_columns = [
        "shape",
        "untreated_froude",
        "oil_viscosity",
        "untreated_ift",
        "oil_density",
        "momentum_amplification",
        "kinetic_power_ratio",
    ]

    required_columns = [
        "experiment_id",
        "oil_id",
        "nozzle_diameter",
        "has_gas",
        "untreated_gas_void_fraction",
        *positive_columns,
    ]

    missing = [column for column in required_columns if column not in ssmd.columns]

    if missing:
        raise ValueError(
            "Missing columns for SSMD physical model comparison: " f"{missing}"
        )

    for column in positive_columns:
        values = ssmd[column].to_numpy(dtype=float)

        invalid = ~np.isfinite(values) | (values <= 0.0)

        if invalid.any():
            raise ValueError(f"Invalid positive values in {column!r}.")

        ssmd[f"log_{column}"] = np.log(ssmd[column])

    gas_void_fraction = ssmd["untreated_gas_void_fraction"].to_numpy(dtype=float)

    if not np.isfinite(gas_void_fraction).all():
        raise ValueError("Invalid untreated gas void fraction.")

    return ssmd.sort_values(
        [
            "oil_id",
            "nozzle_diameter",
            "has_gas",
        ]
    ).reset_index(drop=True)


def _fit_linear_diagnostic_model(
    data: pd.DataFrame,
    *,
    predictors: list[str],
) -> dict[str, float | int]:
    y = data["log_shape"].to_numpy(dtype=float)

    if predictors:
        x_predictors = data[predictors].to_numpy(dtype=float)

        if not np.isfinite(x_predictors).all():
            raise ValueError("Non-finite predictor values found.")

        x = np.column_stack(
            [
                np.ones(len(data)),
                x_predictors,
            ]
        )
    else:
        x = np.ones(
            (
                len(data),
                1,
            ),
            dtype=float,
        )

    coefficients, *_ = np.linalg.lstsq(
        x,
        y,
        rcond=None,
    )

    prediction = x @ coefficients

    residual = y - prediction

    ss_res = np.sum(residual**2)

    ss_tot = np.sum((y - np.mean(y)) ** 2)

    r_squared = 1.0 - ss_res / ss_tot

    n = len(data)

    n_predictors = len(predictors)

    if n_predictors == 0:
        adjusted_r_squared = r_squared
    else:
        adjusted_r_squared = 1.0 - (1.0 - r_squared) * (n - 1) / (n - n_predictors - 1)

    log_rmse = np.sqrt(np.mean(residual**2))

    return {
        "n": n,
        "n_predictors": n_predictors,
        "n_parameters": (n_predictors + 1),
        "r_squared": r_squared,
        "adjusted_r_squared": (adjusted_r_squared),
        "log_rmse": log_rmse,
    }


def compare_ssmd_physical_models(
    data: pd.DataFrame,
) -> pd.DataFrame:
    ssmd = prepare_ssmd_physical_model_data(data)

    rows = []

    for model_name, predictors in SSMD_PHYSICAL_MODEL_SPECS.items():
        metrics = _fit_linear_diagnostic_model(
            ssmd,
            predictors=predictors,
        )

        rows.append(
            {
                "model": model_name,
                **metrics,
            }
        )

    result = pd.DataFrame(rows)

    baseline_r2 = result.loc[
        result["model"].eq("M0 — intercept"),
        "r_squared",
    ].iloc[0]

    m3_r2 = result.loc[
        result["model"].eq("M3 — regime + oil"),
        "r_squared",
    ].iloc[0]

    result["delta_r_squared_vs_m0"] = result["r_squared"] - baseline_r2

    result["delta_r_squared_vs_m3"] = result["r_squared"] - m3_r2

    return result


def _linear_model_prediction(
    data: pd.DataFrame,
    *,
    predictors: list[str],
) -> np.ndarray:
    y = data["log_shape"].to_numpy(dtype=float)

    x_predictors = data[predictors].to_numpy(dtype=float)

    if not np.isfinite(x_predictors).all():
        raise ValueError("Non-finite predictor values found.")

    x = np.column_stack(
        [
            np.ones(len(data)),
            x_predictors,
        ]
    )

    coefficients, *_ = np.linalg.lstsq(
        x,
        y,
        rcond=None,
    )

    return x @ coefficients


def build_ssmd_m4_residuals(
    data: pd.DataFrame,
) -> pd.DataFrame:
    ssmd = prepare_ssmd_physical_model_data(data)

    ssmd["experimental_regime"] = _ssmd_regime_labels(ssmd)

    prediction = _linear_model_prediction(
        ssmd,
        predictors=SSMD_M4_PREDICTORS,
    )

    ssmd["predicted_log_shape"] = prediction

    ssmd["log_shape_residual"] = ssmd["log_shape"] - ssmd["predicted_log_shape"]

    ssmd["predicted_shape"] = np.exp(ssmd["predicted_log_shape"])

    return ssmd


def summarize_ssmd_m4_residuals(
    data: pd.DataFrame,
) -> pd.DataFrame:
    residuals = build_ssmd_m4_residuals(data)

    summary = residuals.groupby(
        [
            "oil_id",
            "experimental_regime",
        ],
        as_index=False,
    ).agg(
        n=(
            "experiment_id",
            "size",
        ),
        mean_log_residual=(
            "log_shape_residual",
            "mean",
        ),
        std_log_residual=(
            "log_shape_residual",
            "std",
        ),
    )

    return summary


def build_ssmd_m4_residual_matrix(
    data: pd.DataFrame,
) -> pd.DataFrame:
    summary = summarize_ssmd_m4_residuals(data)

    regime_order = [
        "2 mm — no gas",
        "3 mm — no gas",
        "2 mm — gas",
    ]

    matrix = summary.pivot(
        index="oil_id",
        columns="experimental_regime",
        values="mean_log_residual",
    )

    matrix = matrix.reindex(columns=regime_order)

    matrix["oil_mean"] = matrix.mean(axis=1)

    matrix["regime_range"] = matrix[regime_order].max(axis=1) - matrix[
        regime_order
    ].min(axis=1)

    return matrix
