import jax.numpy as jnp
from jax import lax


def calculate_d_pred(
    we,
    ca,
    a,
    b,
    max_iter: int = 30,
):
    we_safe = we + 1e-10

    d_initial = a * we_safe ** (-3.0 / 5.0)

    def update(_, d_current):
        return a * (we_safe / (1.0 + b * ca * d_current ** (1.0 / 3.0))) ** (-3.0 / 5.0)

    return lax.fori_loop(
        0,
        max_iter,
        update,
        d_initial,
    )
