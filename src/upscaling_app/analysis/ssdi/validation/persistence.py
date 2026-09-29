from pathlib import Path

import pandas as pd

from upscaling_app import paths


def _load_workbook(
    path: Path,
) -> dict[str, pd.DataFrame]:
    if not path.exists():
        return {}

    workbook = pd.ExcelFile(path)

    return {
        sheet_name: pd.read_excel(
            path,
            sheet_name=sheet_name,
        )
        for sheet_name in workbook.sheet_names
    }


def _save_tables(
    tables: dict[str, pd.DataFrame],
) -> None:
    output = paths.SSDI_VALIDATION_RESULTS_PATH

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    existing = _load_workbook(
        output,
    )

    existing.update(
        tables,
    )

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:
        for sheet_name, table in existing.items():
            table.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False,
            )


def save_loo_result(
    *,
    name: str,
    folds: pd.DataFrame,
    predictions: pd.DataFrame,
    global_metrics: dict[str, float],
    oil_metrics: pd.DataFrame,
) -> None:
    global_table = pd.DataFrame(
        [
            {
                "validation": name,
                "n": len(predictions),
                **global_metrics,
            }
        ]
    )

    _save_tables(
        {
            f"{name}_folds": folds,
            f"{name}_predictions": predictions,
            f"{name}_global": global_table,
            f"{name}_oil": oil_metrics,
        }
    )


def save_excluded_challenge_result(
    *,
    calibration: pd.DataFrame,
    predictions: pd.DataFrame,
    global_metrics: dict[str, float],
    oil_metrics: pd.DataFrame,
) -> None:
    global_table = pd.DataFrame(
        [
            {
                "validation": "excluded_challenge",
                "n": len(predictions),
                **global_metrics,
            }
        ]
    )

    _save_tables(
        {
            "excluded_challenge_calibration": calibration,
            "excluded_challenge_predictions": predictions,
            "excluded_challenge_global": global_table,
            "excluded_challenge_oil": oil_metrics,
        }
    )


def load_validation_global(
    sheet_name: str,
) -> pd.DataFrame:
    path = paths.SSDI_VALIDATION_RESULTS_PATH

    if not path.exists():
        raise FileNotFoundError(f"Validation results not found: {path}")

    try:
        return pd.read_excel(
            path,
            sheet_name=sheet_name,
        )
    except ValueError as exc:
        raise ValueError(
            f"Validation sheet {sheet_name!r} not found. "
            "Run the corresponding validation workflow first."
        ) from exc


def save_validation_comparison(
    comparison: pd.DataFrame,
) -> None:
    _save_tables(
        {
            "validation_comparison": comparison,
        }
    )
