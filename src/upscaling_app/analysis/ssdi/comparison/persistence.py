import pandas as pd

from upscaling_app import paths


def save_model_comparison(
    comparison: pd.DataFrame,
) -> None:
    output = paths.SSDI_COMPARISON_RESULTS_PATH

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:
        comparison.to_excel(
            writer,
            sheet_name="comparison",
            index=False,
        )
