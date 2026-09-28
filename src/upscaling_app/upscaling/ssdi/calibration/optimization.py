import jax

jax.config.update("jax_enable_x64", True)

import jax.numpy as jnp
import numpy as np
from scipy.optimize import minimize

from scipy.optimize import least_squares

from upscaling_app.upscaling.ssdi.physics.model import (
    calculate_d_pred,
    calculate_d_pred_newton,
)


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


@jax.jit
def loss_fn_newton(params, we, ca, d_exp):
    a, b = params

    d_pred = calculate_d_pred_newton(
        we,
        ca,
        a,
        b,
    )

    log_error = jnp.log(d_exp) - jnp.log(d_pred)

    return jnp.mean(log_error**2)


loss_and_grad_newton = jax.jit(jax.value_and_grad(loss_fn_newton))


def optimize_coefficients(
    we,
    ca,
    d_exp,
    a_initial: float,
    b_initial: float,
    b_bounds: tuple[
        float | None,
        float | None,
    ] = (1e-3, None),
    solver: str = "fixed_point",
) -> tuple[float, float, float]:
    we = jnp.asarray(we, dtype=jnp.float64)
    ca = jnp.asarray(ca, dtype=jnp.float64)
    d_exp = jnp.asarray(d_exp, dtype=jnp.float64)

    if solver == "fixed_point":
        loss_gradient = loss_and_grad
    elif solver == "newton":
        loss_gradient = loss_and_grad_newton
    else:
        raise ValueError(f"Unknown SSDI solver: {solver!r}")

    def objective(params):
        loss, gradient = loss_gradient(
            jnp.asarray(params, dtype=jnp.float64),
            we,
            ca,
            d_exp,
        )

        return (
            float(loss),
            np.asarray(gradient, dtype=float),
        )

    initial_guess = np.array(
        [a_initial, b_initial],
        dtype=float,
    )

    bounds = [
        (1e-3, None),
        b_bounds,
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


def optimize_coefficients_oil_wise(
    we,
    ca,
    d_exp,
    a_initial: float,
    b_initial: float,
) -> tuple[float, float, float]:
    we = jnp.asarray(
        we,
        dtype=jnp.float64,
    )
    ca = jnp.asarray(
        ca,
        dtype=jnp.float64,
    )
    d_exp = np.asarray(
        d_exp,
        dtype=float,
    )

    def residuals(params):
        a, b = params

        d_pred = np.asarray(
            calculate_d_pred_newton(
                we,
                ca,
                a,
                b,
            ),
            dtype=float,
        )

        if not np.all(np.isfinite(d_pred)) or np.any(d_pred <= 0.0):
            return np.full(
                d_exp.shape,
                1e6,
                dtype=float,
            )

        return np.log(d_exp) - np.log(d_pred)

    initial_guess = np.array(
        [
            a_initial,
            b_initial,
        ],
        dtype=float,
    )

    initial_residuals = residuals(initial_guess)

    initial_loss = float(np.mean(initial_residuals**2))

    result = least_squares(
        residuals,
        initial_guess,
        bounds=(
            [1e-3, -0.5],
            [np.inf, 1.0],
        ),
        x_scale="jac",
        xtol=1e-10,
        ftol=1e-10,
        gtol=1e-10,
        max_nfev=5000,
    )

    if not result.success:
        raise RuntimeError("Oil-wise SSDI optimization failed: " f"{result.message}")

    log_mse = float(np.mean(result.fun**2))

    if log_mse > initial_loss:
        raise RuntimeError(
            "Oil-wise optimization returned a worse " "solution than the initial guess."
        )

    return (
        float(result.x[0]),
        float(result.x[1]),
        log_mse,
    )
