import pandas as pd

from upscaling_app import paths


import pandas as pd

from upscaling_app import paths


def save_ssdi_analysis(
    results: pd.DataFrame,
    model_version: str,
) -> None:
    paths.RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = paths.RESULTS_DIR / f"ssdi_analysis_{model_version}.xlsx"

    results.to_excel(
        output_path,
        index=False,
    )


def save_model_comparison(
    comparison: pd.DataFrame,
) -> None:
    paths.RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = paths.RESULTS_DIR / "ssdi_model_comparison.xlsx"

    comparison.to_excel(
        output_path,
        index=False,
    )


def save_oil_metrics(
    oil_metrics: pd.DataFrame,
    model_version: str,
) -> None:
    paths.RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = paths.RESULTS_DIR / f"ssdi_oil_metrics_{model_version}.xlsx"

    oil_metrics.to_excel(
        output_path,
        index=False,
    )


def save_leave_one_oil_out(
    result,
) -> None:
    paths.RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = paths.RESULTS_DIR / "ssdi_leave_one_oil_out.xlsx"

    global_metrics = pd.DataFrame([result.global_metrics])

    with pd.ExcelWriter(output_path) as writer:
        result.folds.to_excel(
            writer,
            sheet_name="folds",
            index=False,
        )

        result.predictions.to_excel(
            writer,
            sheet_name="predictions",
            index=False,
        )

        global_metrics.to_excel(
            writer,
            sheet_name="global_metrics",
            index=False,
        )


def save_evaluation_comparison(
    comparison: pd.DataFrame,
) -> None:
    paths.RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = paths.RESULTS_DIR / "ssdi_evaluation_comparison.xlsx"

    comparison.to_excel(
        output_path,
        index=False,
    )
