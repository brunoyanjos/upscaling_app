import jax
import jax.numpy as jnp
import numpy as np
from scipy.optimize import minimize

from upscaling_app.upscaling.ssdi.physics.model import calculate_d_pred


@jax.jit
def loss_fn(params, we, ca, d_exp):
    a, b = params

    d_pred = calculate_d_pred(
        we,
        ca,
        a,
        b,
    )

    log_error = jnp.log(d_exp) - jnp.log(d_pred)

    return jnp.mean(log_error**2)


loss_and_grad = jax.jit(jax.value_and_grad(loss_fn))


def optimize_coefficients(
    we,
    ca,
    d_exp,
    a_initial: float,
    b_initial: float,
) -> tuple[float, float, float]:
    def objective(params):
        loss, gradient = loss_and_grad(
            jnp.asarray(params),
            we,
            ca,
            d_exp,
        )

        return float(loss), np.asarray(gradient, dtype=float)

    initial_guess = np.array(
        [a_initial, b_initial],
        dtype=float,
    )

    bounds = [
        (1e-3, None),
        (1e-3, None),
    ]

    result = minimize(
        objective,
        initial_guess,
        method="L-BFGS-B",
        jac=True,
        bounds=bounds,
    )

    return (
        float(result.x[0]),
        float(result.x[1]),
        float(result.fun),
    )
