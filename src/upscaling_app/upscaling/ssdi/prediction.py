import numpy as np
import pandas as pd

from upscaling_app.upscaling.ssdi.physics.model import (
    calculate_d_pred,
)

from upscaling_app.upscaling.ssdi.physics.derived_properties import (
    add_ssdi_physics,
)


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


def predict_field_ssdi(
    scenario: dict[str, float],
    a: float,
    b: float,
) -> dict[str, float]:
    """Predict field-scale SSDI D50 from inputs expressed in SI."""

    positive = (
        "nozzle_diameter",
        "oil_flow",
        "oil_density",
        "oil_viscosity",
        "ift",
    )

    for key in positive:
        value = float(scenario[key])
        if not np.isfinite(value) or value <= 0:
            raise ValueError(f"{key} must be finite and positive.")

    gas_flow = float(scenario["gas_flow"])
    gas_density = float(scenario["gas_density"])

    if not np.isfinite(gas_flow) or gas_flow < 0:
        raise ValueError("Gas flow must be non-negative.")

    if gas_flow > 0 and (not np.isfinite(gas_density) or gas_density <= 0):
        raise ValueError("Gas density is required when gas is present.")

    if not np.isfinite([a, b]).all() or a <= 0:
        raise ValueError("Invalid calibration coefficients.")

    data = add_ssdi_physics(pd.DataFrame([scenario]))

    state = data.iloc[0]

    required = (
        "reduced_gravity",
        "froude",
        "effective_velocity",
        "reynolds",
        "weber",
        "capillary",
    )

    for key in required:
        value = float(state[key])
        if not np.isfinite(value) or value <= 0:
            raise ValueError(f"Invalid physical state: {key} = {value}")

    we = float(state["weber"])
    ca = float(state["capillary"])

    ratio = float(np.asarray(calculate_d_pred(we, ca, a, b)))

    if not np.isfinite(ratio) or ratio <= 0:
        raise ValueError("The SSDI solver returned an invalid D50/D.")

    # Check the residual of the existing iterative formulation.
    k = a ** (5.0 / 3.0) / (we + 1e-10)
    c = k * b * ca
    y = np.cbrt(ratio)

    residual = y**5 - c * y - k
    scale = abs(y**5) + abs(c * y) + abs(k)

    if abs(residual) / max(scale, 1e-12) > 1e-5:
        raise ValueError("The SSDI solver did not converge sufficiently.")

    return {
        "d50_m": ratio * float(scenario["nozzle_diameter"]),
        "d50_over_d": ratio,
        "reynolds": float(state["reynolds"]),
        "weber": we,
        "capillary": ca,
        "void_fraction": float(state["void_fraction"]),
        "effective_velocity": float(state["effective_velocity"]),
    }
