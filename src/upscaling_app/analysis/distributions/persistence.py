import pandas as pd

from upscaling_app import paths


def save_distribution_fit_analysis(
    evaluation: pd.DataFrame,
    cdf_points: pd.DataFrame,
    fit_summary: pd.DataFrame,
    fit_summary_by_regime: pd.DataFrame,
    d50_summary: pd.DataFrame,
) -> None:
    if "experiment_id" not in evaluation.columns:
        raise ValueError("evaluation must contain experiment_id.")

    if evaluation["experiment_id"].duplicated().any():
        raise ValueError(
            "Distribution evaluation contains duplicated experiment_id values."
        )

    path = paths.DISTRIBUTION_FIT_EVALUATION_PATH

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        path,
        engine="openpyxl",
    ) as writer:
        evaluation.to_excel(
            writer,
            sheet_name="evaluation",
            index=False,
        )

        cdf_points.to_excel(
            writer,
            sheet_name="cdf_points",
            index=False,
        )

        fit_summary.to_excel(
            writer,
            sheet_name="fit_summary",
            index=False,
        )

        fit_summary_by_regime.to_excel(
            writer,
            sheet_name="fit_by_regime",
            index=False,
        )

        d50_summary.to_excel(
            writer,
            sheet_name="d50_summary",
            index=False,
        )
