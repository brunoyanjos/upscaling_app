import numpy as np
import pandas as pd

from upscaling_app.upscaling.ssdi.physics.model import calculate_d_pred


def predict_ssdi(
    experiments: pd.DataFrame,
    we,
    ca,
    a: float,
    b: float,
    model_version: str,
) -> pd.DataFrame:
    d50_d_exp = (
        experiments["measured_d50"] / experiments["nozzle_diameter"]
    ).to_numpy()

    d50_d_pred = np.asarray(
        calculate_d_pred(
            we,
            ca,
            a,
            b,
        )
    )

    return pd.DataFrame(
        {
            "experiment_id": experiments["experiment_id"].to_numpy(),
            "model_version": model_version,
            "a_coef": a,
            "b_coef": b,
            "d50_D_exp": d50_d_exp,
            "d50_D_pred": d50_d_pred,
            "d50_exp": experiments["measured_d50"].to_numpy(),
            "d50_pred": (d50_d_pred * experiments["nozzle_diameter"].to_numpy()),
        }
    )
