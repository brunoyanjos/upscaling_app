import pandas as pd

from upscaling_app import paths


def save_distribution_fit_evaluation(
    evaluation: pd.DataFrame,
) -> None:
    if "experiment_id" not in evaluation.columns:
        raise ValueError("evaluation must contain experiment_id.")

    if evaluation["experiment_id"].duplicated().any():
        raise ValueError(
            "Distribution evaluation contains duplicated " "experiment_id values."
        )

    path = paths.DISTRIBUTION_FIT_EVALUATION_PATH

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    evaluation.to_excel(
        path,
        index=False,
    )


def save_distribution_method_comparison(
    global_summary: pd.DataFrame,
    paired_comparison: pd.DataFrame,
    by_regime: pd.DataFrame,
    statistical_tests: pd.DataFrame,
) -> None:
    path = paths.DISTRIBUTION_METHOD_COMPARISON_PATH

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        path,
        engine="openpyxl",
    ) as writer:
        global_summary.to_excel(
            writer,
            sheet_name="global_summary",
            index=False,
        )

        paired_comparison.to_excel(
            writer,
            sheet_name="paired_comparison",
            index=False,
        )

        by_regime.to_excel(
            writer,
            sheet_name="by_regime",
            index=False,
        )

        statistical_tests.to_excel(
            writer,
            sheet_name="statistical_tests",
            index=False,
        )
