from __future__ import annotations

import pandas as pd

from upscaling_app import paths
from upscaling_app.analysis.distributions.correlation.plotting import (
    save_ssdi_shape_relations,
    save_ssmd_shape_relations,
    save_untreated_shape_relations,
)

from upscaling_app.upscaling.distributions.correlation.data import (
    load_distribution_correlation_dataset,
)
from upscaling_app.upscaling.distributions.correlation.features import (
    RELEASE_FEATURE_COLUMNS,
    SSMD_FEATURE_COLUMNS,
    build_distribution_correlation_features,
)
from upscaling_app.analysis.distributions.correlation.analysis import (
    build_ssmd_m4_residual_matrix,
    compare_ssmd_physical_models,
    decompose_ssmd_shape_variance,
    prepare_ssmd_within_group_data,
    screen_predictor_redundancy,
    screen_shape_correlations,
    screen_ssmd_within_group_relations,
)


def print_header(
    title: str,
    *,
    width: int = 120,
) -> None:
    print()
    print(title)
    print("-" * width)


def check_shape_correlation_screening(
    data: pd.DataFrame,
) -> pd.DataFrame:
    screening = screen_shape_correlations(data)

    print_header("Shape correlation screening")

    population_order = [
        "Untreated",
        "SSDI",
        "SSMD",
    ]

    for population in population_order:
        subset = screening.loc[
            screening["population"].eq(population),
            [
                "feature",
                "n",
                "n_unique",
                "spearman_rho",
                "abs_spearman_rho",
            ],
        ]

        print()
        print(population)
        print("-" * 100)

        print(
            subset.to_string(
                index=False,
                float_format=lambda value: (f"{value:.6f}"),
            )
        )

    return screening


def check_base_dataset() -> pd.DataFrame:
    data = load_distribution_correlation_dataset()

    print_header("Distribution correlation base dataset")

    print(f"Rows                  : " f"{len(data)}")

    print(f"Unique experiment IDs : " f"{data['experiment_id'].nunique()}")

    print(f"Unique oils           : " f"{data['oil_id'].nunique()}")

    print()
    print("By dispersion kind")

    print(data["dispersion_kind"].value_counts().to_string())

    print()
    print("Shape range")

    print(f"{data['shape'].min():.6f}" " → " f"{data['shape'].max():.6f}")

    return data


def check_feature_dataset() -> pd.DataFrame:
    data = build_distribution_correlation_features()

    print_header("Distribution correlation feature dataset")

    print(f"Rows                  : " f"{len(data)}")

    print(f"Unique experiment IDs : " f"{data['experiment_id'].nunique()}")

    print(f"Unique oils           : " f"{data['oil_id'].nunique()}")

    print()
    print("By dispersion kind")

    print(data["dispersion_kind"].value_counts().to_string())

    print_header("Release features")

    release_rows = []

    for column in RELEASE_FEATURE_COLUMNS:
        release_rows.append(
            {
                "feature": column,
                "missing": (data[column].isna().sum()),
                "minimum": (data[column].min()),
                "maximum": (data[column].max()),
            }
        )

    release_summary = pd.DataFrame(release_rows)

    print(
        release_summary.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6g}"),
        )
    )

    print_header("SSMD-specific features")

    ssmd_rows = []

    for column in SSMD_FEATURE_COLUMNS:
        ssmd_rows.append(
            {
                "feature": column,
                "non_null": (data[column].notna().sum()),
                "missing": (data[column].isna().sum()),
            }
        )

    ssmd_summary = pd.DataFrame(ssmd_rows)

    print(ssmd_summary.to_string(index=False))

    print_header("Shape")

    print(f"min={data['shape'].min():.6f}  " f"max={data['shape'].max():.6f}")

    return data


def check_expected_structure(
    data: pd.DataFrame,
) -> None:
    print_header("Structural checks")

    expected_rows = 180

    expected_counts = {
        "Untreated": 30,
        "SSDI": 60,
        "SSMD": 90,
    }

    actual_counts = data["dispersion_kind"].value_counts().to_dict()

    checks = {
        "rows": (len(data) == expected_rows),
        "unique_experiment_ids": (data["experiment_id"].nunique() == expected_rows),
        "unique_oils": (data["oil_id"].nunique() == 10),
        "dispersion_counts": (actual_counts == expected_counts),
        "release_features_complete": (
            not data[RELEASE_FEATURE_COLUMNS].isna().any().any()
        ),
        "ssmd_features_complete": (
            not data.loc[
                data["dispersion_kind"].eq("SSMD"),
                SSMD_FEATURE_COLUMNS,
            ]
            .isna()
            .any()
            .any()
        ),
    }

    for name, passed in checks.items():
        status = "PASS" if passed else "FAIL"

        print(f"{name:30s} : " f"{status}")

    if not all(checks.values()):
        raise RuntimeError("Distribution correlation reference " "check failed.")


def check_predictor_redundancy(
    data: pd.DataFrame,
    *,
    threshold: float = 0.80,
) -> pd.DataFrame:
    redundancy = screen_predictor_redundancy(data)

    print_header("Predictor redundancy screening")

    population_order = [
        "Untreated",
        "SSDI",
        "SSMD",
    ]

    for population in population_order:
        subset = redundancy.loc[
            redundancy["population"].eq(population)
            & (redundancy["abs_spearman_rho"] >= threshold),
            [
                "feature_a",
                "feature_b",
                "n",
                "spearman_rho",
            ],
        ]

        print()
        print(f"{population} " f"(|rho| >= {threshold:.2f})")
        print("-" * 100)

        if subset.empty:
            print("No strongly redundant " "predictor pairs.")
            continue

        print(
            subset.to_string(
                index=False,
                float_format=lambda value: (f"{value:.6f}"),
            )
        )

    return redundancy


def check_ssmd_within_group_relations(
    data: pd.DataFrame,
) -> pd.DataFrame:
    centered = prepare_ssmd_within_group_data(data)

    screening = screen_ssmd_within_group_relations(data)

    print_header("SSMD within-group physical screening")

    print(f"Experiments : {len(centered)}")

    print("Groups      : " f"{centered.groupby(
            ['oil_id', 'nozzle_diameter', 'has_gas']
        ).ngroups}")

    print("Observations per group : " f"{centered.groupby(
            ['oil_id', 'nozzle_diameter', 'has_gas']
        ).size().unique().tolist()}")

    print()

    print(
        screening.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )

    return screening


def save_candidate_relation_plots(
    data: pd.DataFrame,
) -> None:
    print_header("Candidate physical relation plots")

    output_dir = paths.DISTRIBUTION_CORRELATION_FIGURES_DIR

    save_untreated_shape_relations(
        data=data,
        output_dir=output_dir,
    )

    save_ssdi_shape_relations(
        data=data,
        output_dir=output_dir,
    )

    save_ssmd_shape_relations(
        data=data,
        output_dir=output_dir,
    )

    print(f"Figures saved to: " f"{output_dir}")


def check_ssmd_shape_variance_decomposition(
    data: pd.DataFrame,
) -> pd.DataFrame:
    decomposition = decompose_ssmd_shape_variance(data)

    print_header("SSMD log(k) variance decomposition")

    print(
        decomposition.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )

    return decomposition


def check_ssmd_physical_model_comparison(
    data: pd.DataFrame,
) -> pd.DataFrame:
    comparison = compare_ssmd_physical_models(data)

    print_header("SSMD physical model comparison")

    print(
        comparison.to_string(
            index=False,
            float_format=lambda value: (f"{value:.6f}"),
        )
    )

    print()
    print("Categorical diagnostic references")
    print("oil + regime : R² = 0.432043")
    print("oil × regime : R² = 0.683445")
    print("upper diagnostic with treatment : " "R² ≈ 0.722")

    return comparison


def check_ssmd_m4_residual_structure(
    data: pd.DataFrame,
) -> pd.DataFrame:
    matrix = build_ssmd_m4_residual_matrix(data)

    print_header("SSMD M4 residual structure")

    print(
        matrix.to_string(
            float_format=lambda value: (f"{value:+.6f}"),
        )
    )

    return matrix


def main() -> None:
    check_base_dataset()

    features = check_feature_dataset()

    check_expected_structure(features)

    check_shape_correlation_screening(features)

    check_predictor_redundancy(features)

    save_candidate_relation_plots(features)

    check_ssmd_within_group_relations(features)

    check_ssmd_shape_variance_decomposition(features)

    check_ssmd_physical_model_comparison(features)

    check_ssmd_m4_residual_structure(features)


if __name__ == "__main__":
    main()
