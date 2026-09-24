import numpy as np
import pandas as pd


import pandas as pd


def compare_distribution_d50(
    summary: pd.DataFrame,
    experiments: pd.DataFrame,
) -> pd.DataFrame:
    comparison = summary[
        [
            "experiment_id",
            "d50",
        ]
    ].merge(
        experiments[
            [
                "experiment_id",
                "oil_id",
                "dispersion_tag",
                "nozzle_diameter",
                "has_gas",
                "measured_d50",
                "source_sheet",
            ]
        ],
        on="experiment_id",
        how="left",
        validate="one_to_one",
    )

    comparison["d50_error"] = comparison["d50"] - comparison["measured_d50"]

    comparison["d50_relative_error"] = (
        comparison["d50_error"] / comparison["measured_d50"]
    )

    return comparison
