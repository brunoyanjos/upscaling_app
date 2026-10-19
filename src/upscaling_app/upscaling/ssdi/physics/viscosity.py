import numpy as np


def estimate_stabilized_viscosity(
    temperature_c: float,
    viscosities_pa_s: tuple[float, float, float],
) -> float:
    """Interpolate stabilized-oil dynamic viscosity in Pa.s.

    Reference temperatures: 20, 40 and 50 degrees Celsius.
    Piecewise interpolation of ln(mu) against inverse
    absolute temperature.
    """

    temperatures = np.array([20.0, 40.0, 50.0])
    viscosities = np.asarray(viscosities_pa_s, dtype=float)

    if not np.isfinite(temperature_c):
        raise ValueError("Temperature must be finite.")

    if not 20.0 <= temperature_c <= 50.0:
        raise ValueError(
            "Temperature must be between 20 and 50°C. " "Extrapolation is not enabled."
        )

    if (
        viscosities.shape != (3,)
        or not np.isfinite(viscosities).all()
        or (viscosities <= 0).any()
    ):
        raise ValueError("Invalid reference viscosities.")

    inverse_temperature = 1.0 / (temperatures + 273.15)

    log_viscosity = np.interp(
        1.0 / (temperature_c + 273.15),
        inverse_temperature[::-1],
        np.log(viscosities)[::-1],
    )

    return float(np.exp(log_viscosity))
