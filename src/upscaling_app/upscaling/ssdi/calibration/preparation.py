import jax.numpy as jnp
import pandas as pd


def prepare_calibration_arrays(
    experiments: pd.DataFrame,
) -> tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    we = jnp.asarray(experiments["weber"].to_numpy())
    ca = jnp.asarray(experiments["capillary"].to_numpy())

    d50_d = jnp.asarray(
        (experiments["measured_d50"] / experiments["nozzle_diameter"]).to_numpy()
    )

    return we, ca, d50_d
