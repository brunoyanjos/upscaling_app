import jax
import jax.numpy as jnp

from upscaling_app.upscaling.ssdi.physics.model import calculate_d_pred


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

    return jnp.mean(jnp.abs(d_pred - d_exp))


evaluate_all_combinations = jax.vmap(
    evaluate_residual_value,
    in_axes=(None, None, None, 0, 0),
)

evaluate_optimized = jax.jit(evaluate_all_combinations)


def estimate_initial_coefficients(
    we,
    ca,
    d_exp,
) -> tuple[float, float]:
    a_values = jnp.arange(1.0, 201.0, 1.0)
    b_values = jnp.linspace(0.01, 1.0, 1000)

    a_grid, b_grid = jnp.meshgrid(
        a_values,
        b_values,
        indexing="ij",
    )

    a_flat = a_grid.ravel()
    b_flat = b_grid.ravel()

    errors = evaluate_optimized(
        we,
        ca,
        d_exp,
        a_flat,
        b_flat,
    )

    best_index = jnp.nanargmin(errors)

    return (
        float(a_flat[best_index]),
        float(b_flat[best_index]),
    )
