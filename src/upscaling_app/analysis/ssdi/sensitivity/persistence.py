import pandas as pd

from upscaling_app import paths


def save_sensitivity_result(
    *,
    name: str,
    summary: pd.DataFrame,
    excluded: pd.DataFrame,
) -> None:
    output = paths.SSDI_SENSITIVITY_RESULTS_PATH

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_sheet = f"{name}_summary"
    excluded_sheet = f"{name}_excluded"

    if output.exists():
        writer_kwargs = {
            "engine": "openpyxl",
            "mode": "a",
            "if_sheet_exists": "replace",
        }
    else:
        writer_kwargs = {
            "engine": "openpyxl",
            "mode": "w",
        }

    with pd.ExcelWriter(
        output,
        **writer_kwargs,
    ) as writer:
        summary.to_excel(
            writer,
            sheet_name=summary_sheet,
            index=False,
        )

        excluded.to_excel(
            writer,
            sheet_name=excluded_sheet,
            index=False,
        )
