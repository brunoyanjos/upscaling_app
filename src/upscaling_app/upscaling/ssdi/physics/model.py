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


def calculate_d_pred_newton(
    we,
    ca,
    a,
    b,
    max_iter: int = 30,
):
    we_safe = we + 1e-10

    k = a ** (5.0 / 3.0) / we_safe
    c = k * b * ca

    y_base = k ** (1.0 / 5.0)

    y_initial = y_base + jnp.maximum(c, 0.0) ** (1.0 / 4.0)
    y_initial = lax.stop_gradient(y_initial)

    def update(_, y_current):
        residual = y_current**5 - c * y_current - k

        derivative = 5.0 * y_current**4 - c

        return y_current - residual / derivative

    y = lax.fori_loop(
        0,
        max_iter,
        update,
        y_initial,
    )

    return y**3
