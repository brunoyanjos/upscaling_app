import jax
import jax.numpy as jnp

from upscaling_app.upscaling.ssdi.physics.model import (
    calculate_d_pred,
    calculate_d_pred_newton,
)


def evaluate_residual_value(
    we,
    ca,
    d_exp,
    a,
    b,
):
    d_pred = calculate_d_pred(
        we,
        ca,
        a,
        b,
    )

    error = jnp.mean(jnp.abs(d_pred - d_exp))

    valid = jnp.all(jnp.isfinite(d_pred) & (d_pred > 0.0))

    return jnp.where(
        valid,
        error,
        jnp.inf,
    )


def evaluate_residual_value_newton(
    we,
    ca,
    d_exp,
    a,
    b,
):
    d_pred = calculate_d_pred_newton(
        we,
        ca,
        a,
        b,
    )

    error = jnp.mean(jnp.abs(d_pred - d_exp))

    valid = jnp.all(jnp.isfinite(d_pred) & (d_pred > 0.0))

    return jnp.where(
        valid,
        error,
        jnp.inf,
    )


evaluate_all_combinations = jax.vmap(
    evaluate_residual_value,
    in_axes=(None, None, None, 0, 0),
)

evaluate_all_combinations_newton = jax.vmap(
    evaluate_residual_value_newton,
    in_axes=(None, None, None, 0, 0),
)

evaluate_optimized = jax.jit(evaluate_all_combinations)

evaluate_optimized_newton = jax.jit(evaluate_all_combinations_newton)


def estimate_initial_coefficients(
    we,
    ca,
    d_exp,
    b_min: float = 0.01,
    b_max: float = 1.0,
    solver: str = "fixed_point",
) -> tuple[float, float]:
    a_values = jnp.arange(
        1.0,
        201.0,
        1.0,
    )

    b_values = jnp.linspace(
        b_min,
        b_max,
        1000,
    )

    a_grid, b_grid = jnp.meshgrid(
        a_values,
        b_values,
        indexing="ij",
    )

    a_flat = a_grid.ravel()
    b_flat = b_grid.ravel()

    if solver == "fixed_point":
        evaluator = evaluate_optimized
    elif solver == "newton":
        evaluator = evaluate_optimized_newton
    else:
        raise ValueError(f"Unknown SSDI solver: {solver!r}")

    errors = evaluator(
        we,
        ca,
        d_exp,
        a_flat,
        b_flat,
    )

    best_index = jnp.argmin(errors)

    return (
        float(a_flat[best_index]),
        float(b_flat[best_index]),
    )
