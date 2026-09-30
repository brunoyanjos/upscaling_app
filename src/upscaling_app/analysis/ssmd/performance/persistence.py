from __future__ import annotations

import pandas as pd

from upscaling_app import paths

RESULT_KEYS = [
    "ssmd_model_version",
    "ssdi_source_version",
    "evaluation_target",
]


def _require_columns(
    data: pd.DataFrame,
    columns: list[str],
) -> None:
    missing = [column for column in columns if column not in data.columns]

    if missing:
        raise ValueError(
            f"SSMD performance results are missing required columns: {missing}"
        )


def _validate_results(
    results: pd.DataFrame,
) -> None:
    if results.empty:
        raise ValueError("SSMD performance results cannot be empty.")

    _require_columns(
        results,
        [
            *RESULT_KEYS,
            "n",
            "log_mse",
            "r2_log",
            "rmse",
            "mape_pct",
            "mean_log_residual",
            "std_log_residual",
        ],
    )

    duplicated = results.duplicated(
        subset=RESULT_KEYS,
        keep=False,
    )

    if duplicated.any():
        duplicate_rows = results.loc[
            duplicated,
            RESULT_KEYS,
        ]

        raise ValueError(
            "Duplicate SSMD performance results found:\n"
            f"{duplicate_rows.to_string(index=False)}"
        )


def save_performance_results(
    results: pd.DataFrame,
) -> None:
    _validate_results(
        results,
    )

    output = paths.SSMD_PERFORMANCE_RESULTS_PATH

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_versions = results["ssdi_source_version"].dropna().unique()

    if len(source_versions) != 1:
        raise ValueError(
            "A performance run must contain exactly one SSDI source version."
        )

    source_version = source_versions[0]

    if output.exists():
        existing = pd.read_excel(
            output,
        )

        _validate_results(
            existing,
        )

        existing = existing.loc[~existing["ssdi_source_version"].eq(source_version)]

        combined = pd.concat(
            [
                existing,
                results,
            ],
            ignore_index=True,
        )

    else:
        combined = results.copy()

    _validate_results(
        combined,
    )

    combined = combined.sort_values(
        [
            "ssdi_source_version",
            "evaluation_target",
            "ssmd_model_version",
        ]
    ).reset_index(
        drop=True,
    )

    combined.to_excel(
        output,
        index=False,
    )
