from pathlib import Path

import pandas as pd

from upscaling_app import paths


def _load_sheet(
    path: Path,
    sheet_name: str,
) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_excel(
            path,
            sheet_name=sheet_name,
        )
    except ValueError:
        return pd.DataFrame()


def _replace_model_version(
    existing: pd.DataFrame,
    new_data: pd.DataFrame,
    model_version: str,
) -> pd.DataFrame:
    if existing.empty:
        return new_data.copy()

    if "model_version" not in existing.columns:
        raise ValueError(
            "Existing performance table does not contain " "'model_version'."
        )

    existing = existing.loc[existing["model_version"] != model_version]

    return pd.concat(
        [
            existing,
            new_data,
        ],
        ignore_index=True,
    )


def save_performance_result(
    *,
    model_version: str,
    results: pd.DataFrame,
    global_metrics: dict[str, float],
    oil_metrics: pd.DataFrame,
) -> None:
    output = paths.SSDI_PERFORMANCE_RESULTS_PATH

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    global_row = pd.DataFrame(
        [
            {
                "model_version": model_version,
                "n": len(results),
                **global_metrics,
                "outlier_count": int(results["is_outlier"].sum()),
            }
        ]
    )

    oil_table = oil_metrics.copy()
    oil_table.insert(
        0,
        "model_version",
        model_version,
    )

    residual_table = results.copy()

    global_table = _replace_model_version(
        existing=_load_sheet(
            output,
            "global_metrics",
        ),
        new_data=global_row,
        model_version=model_version,
    )

    oil_table = _replace_model_version(
        existing=_load_sheet(
            output,
            "oil_metrics",
        ),
        new_data=oil_table,
        model_version=model_version,
    )

    residual_table = _replace_model_version(
        existing=_load_sheet(
            output,
            "residuals",
        ),
        new_data=residual_table,
        model_version=model_version,
    )

    global_table = global_table.sort_values(
        "model_version",
    ).reset_index(drop=True)

    oil_table = oil_table.sort_values(
        [
            "model_version",
            "oil_id",
        ]
    ).reset_index(drop=True)

    residual_table = residual_table.sort_values(
        [
            "model_version",
            "oil_id",
            "experiment_id",
        ]
    ).reset_index(drop=True)

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:
        global_table.to_excel(
            writer,
            sheet_name="global_metrics",
            index=False,
        )

        oil_table.to_excel(
            writer,
            sheet_name="oil_metrics",
            index=False,
        )

        residual_table.to_excel(
            writer,
            sheet_name="residuals",
            index=False,
        )
