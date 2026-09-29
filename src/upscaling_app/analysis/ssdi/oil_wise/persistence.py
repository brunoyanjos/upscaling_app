import pandas as pd

from upscaling_app import paths


def save_oil_wise_comparison(
    *,
    overall: pd.DataFrame,
    by_oil: pd.DataFrame,
) -> None:
    output = paths.SSDI_OIL_WISE_RESULTS_PATH

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:
        overall.to_excel(
            writer,
            sheet_name="overall_metrics",
            index=False,
        )

        by_oil.to_excel(
            writer,
            sheet_name="by_oil",
            index=False,
        )
