"""Semantic colour palette used throughout the upscaling application."""

from __future__ import annotations

from typing import Final

SCIENTIFIC_COLORS: Final[dict[str, dict[int, str]]] = {
    "untreated": {
        300: "#6B5A50",
        500: "#3F342E",
        700: "#241C18",
    },
    "ssmd": {
        300: "#A9CDEE",
        500: "#5C98D2",
        700: "#2D679C",
    },
    "ssdi_corexit": {
        300: "#F6BE8B",
        500: "#EB8A2F",
        700: "#C46512",
    },
    "ssdi_finasol": {
        300: "#F3E39B",
        500: "#DFC24A",
        700: "#AF8C17",
    },
}


SSMD_FRACTION_COLORS: Final[dict[float, str]] = {
    0.40: "#B4D2F0",
    0.45: "#8DB9E5",
    0.50: "#5F96CD",
    0.55: "#2F679E",
}


GRAY_COLORS: Final[dict[str, str]] = {
    "dark": "#374151",
    "regression": "#6B7280",
    "medium": "#9CA3AF",
    "identity": "#B9C0C9",
    "light": "#D1D5DB",
    "grid": "#E5E7EB",
    "background": "#F8F9FA",
    "text": "#374151",
}


NOZZLE_DIAMETER_TONES: Final[dict[float, int]] = {
    0.002: 300,
    0.003: 500,
    0.004: 700,
}


REGIME_ALIASES: Final[dict[str, str]] = {
    "untreated": "untreated",
    "ssmd": "ssmd",
    "wj": "ssmd",
    "corexit": "ssdi_corexit",
    "c9500": "ssdi_corexit",
    "ssdi_c9500": "ssdi_corexit",
    "ssdi_corexit": "ssdi_corexit",
    "finasol": "ssdi_finasol",
    "ibc": "ssdi_finasol",
    "ssdi_ibc": "ssdi_finasol",
    "ssdi_finasol": "ssdi_finasol",
}


def _normalize_regime(regime: str) -> str:
    key = regime.strip().lower().replace(" ", "_").replace("-", "_")

    try:
        return REGIME_ALIASES[key]
    except KeyError as exc:
        available = ", ".join(sorted(REGIME_ALIASES))
        raise ValueError(
            f"Unknown regime {regime!r}. Available regimes: {available}."
        ) from exc


def _normalize_nozzle_diameter(diameter: float) -> float:
    value = round(float(diameter), 6)

    if value not in NOZZLE_DIAMETER_TONES:
        available = ", ".join(
            f"{diameter * 1e3:g} mm" for diameter in NOZZLE_DIAMETER_TONES
        )
        raise ValueError(
            f"Unsupported nozzle diameter {diameter!r} m. "
            f"Available diameters: {available}."
        )

    return value


def get_base_color(regime: str) -> str:
    regime_key = _normalize_regime(regime)
    return SCIENTIFIC_COLORS[regime_key][500]


def get_regime_color(
    regime: str,
    *,
    nozzle_diameter: float | None = None,
    tone: int | None = None,
) -> str:
    regime_key = _normalize_regime(regime)

    if nozzle_diameter is not None and tone is not None:
        raise ValueError("Specify either 'nozzle_diameter' or 'tone', not both.")

    if nozzle_diameter is not None:
        diameter = _normalize_nozzle_diameter(nozzle_diameter)
        tone = NOZZLE_DIAMETER_TONES[diameter]

    if tone is None:
        tone = 500

    try:
        return SCIENTIFIC_COLORS[regime_key][tone]
    except KeyError as exc:
        available = ", ".join(str(value) for value in SCIENTIFIC_COLORS[regime_key])
        raise ValueError(
            f"Unsupported tone {tone}. Available tones: {available}."
        ) from exc


def get_ssmd_fraction_color(water_jet_fraction: float) -> str:
    fraction = round(float(water_jet_fraction), 2)

    try:
        return SSMD_FRACTION_COLORS[fraction]
    except KeyError as exc:
        available = ", ".join(f"{value:.0%}" for value in SSMD_FRACTION_COLORS)
        raise ValueError(
            f"Unsupported water-jet fraction {water_jet_fraction!r}. "
            f"Available fractions: {available}."
        ) from exc


def get_gray(name: str) -> str:
    key = name.strip().lower()

    try:
        return GRAY_COLORS[key]
    except KeyError as exc:
        available = ", ".join(GRAY_COLORS)
        raise ValueError(
            f"Unknown grey colour {name!r}. " f"Available colours: {available}."
        ) from exc
